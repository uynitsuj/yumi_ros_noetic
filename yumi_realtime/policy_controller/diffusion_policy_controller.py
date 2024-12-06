from yumi_realtime.controller import YuMiROSInterface
from loguru import logger
import numpy as onp
import tyro
import rospy
from typing import Literal
from yumi_realtime.base import YuMiBaseInterface
from yumi_realtime.policy_controller.utils.utils import *
# from dp_gs.dataset.utils import *
from dp_gs.policy.diffusion_wrapper import DiffusionWrapper
from cv_bridge import CvBridge
from sensor_msgs.msg import Image
from collections import deque
from scipy.spatial.transform import Rotation
import PIL.Image as PILimage
import torch
import time

from line_profiler import LineProfiler

class YuMiDiffusionPolicyController(YuMiROSInterface):
    """YuMi controller for diffusion policy control."""
    
    def __init__(self, ckpt_path: str = None, ckpt_id: int = 0, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._interactive_handles = False
        
        for side in ['left', 'right']:
            target_handle = self.transform_handles[side]
            target_handle.control.visible = False
        
        assert ckpt_path is not None, "Diffusion Policy checkpoint path must be provided."
        
        # Setup Diffusion Policy module and weights
        self.model = DiffusionWrapper(model_ckpt_folder=ckpt_path, ckpt_id=ckpt_id, device='cuda')
        
        # ROS Camera Observation Subscriber
        self.bridge = CvBridge()
        self.height = None
        self.width = None
        
        self.proprio_buffer = deque([],maxlen=self.model.model.obs_horizon)

        self.observation_buffers = {}
        self.camera_buffers = {}
        self.camera_topics = [topic[0] for topic in rospy.get_published_topics() if 'sensor_msgs/Image' in topic[1]]
        
        # Initialize a deque for each camera
        self.max_buffer_size = 5  # For storing recent messages to sync from
        self.main_camera = "camera_0"
        for idx, topic in enumerate(self.camera_topics):
            camera_name = f"camera_{idx}"
            if camera_name == self.main_camera:
                # Main camera's synchronized buffer
                self.observation_buffers[camera_name] = deque([], maxlen=self.model.model.obs_horizon)
            else:
                # Other cameras' message buffers for synchronization
                self.camera_buffers[camera_name] = deque([], maxlen=self.max_buffer_size)
            
        # Subscribe main camera separately since it drives synchronization
        rospy.Subscriber(self.camera_topics[0], Image, self.main_camera_callback)
        
        # Subscribe other cameras
        for idx, topic in enumerate(self.camera_topics[1:], start=1):
            camera_name = f"camera_{idx}"
            rospy.Subscriber(topic, Image, self.camera_callback, callback_args=(camera_name,))
        
        self.cur_proprio = None
        
        self.cartesian_pose_L = None
        self.cartesian_pose_R = None
        
        # Control mode
        # self.control_mode = 'receding_horizon_control'
        self.control_mode = 'temporal_ensemble'
        
        if self.control_mode == 'receding_horizon_control':
            self.action_queue = deque([],maxlen=self.model.model.action_horizon//2)
        elif self.control_mode == 'temporal_ensemble':
            self.action_queue = deque([],maxlen=self.model.model.action_horizon)
        self.prev_action = deque([],maxlen=self.model.model.obs_horizon)
        
        self._setup_scene()
        
        logger.info("Diffusion Policy controller initialized")

        self.gripper_thres = 0.018
    
    def camera_callback(self, image_msg: Image, camera_name: str):
        """Store messages from non-main cameras for synchronization"""
        camera_name = camera_name[0]
        if camera_name not in self.camera_buffers:
            return
        
        self.camera_buffers[camera_name].append(image_msg)
    
    def main_camera_callback(self, image_msg: Image):
        """Synchronize all buffers based on main camera's frequency"""
        if self.height is None and self.width is None:
            self.height = image_msg.height
            self.width = image_msg.width
            logger.info(f"First image received from main camera; Observation dim: {self.height}x{self.width}x3")
        
        if self.cartesian_pose_L is None or self.cartesian_pose_R is None:
            return

        target_time = image_msg.header.stamp.to_nsec()
        
        # Process main camera
        onp_img = self.bridge.imgmsg_to_cv2(image_msg, desired_encoding='rgb8').astype("float32") / 255.0
        new_obs = onp.transpose(onp_img, (2, 0, 1))  # C, H, W
        
        # Get synchronized observations from other cameras
        all_cameras_ready = True
        synced_obs = {self.main_camera: new_obs}
        
        for camera_name, buffer in self.camera_buffers.items():
            if not buffer:  # Skip if buffer is empty
                all_cameras_ready = False
                break
                
            # Find closest message in time
            closest_msg = min(
                buffer,
                key=lambda msg: abs(msg.header.stamp.to_nsec() - target_time)
            )
            onp_img = self.bridge.imgmsg_to_cv2(closest_msg, desired_encoding='rgb8').astype("float32") / 255.0
            synced_obs[camera_name] = onp.transpose(onp_img, (2, 0, 1))
        
        if not all_cameras_ready:
            return
        
        # Update proprioception
        self.update_curr_proprio()
        
        # Update all image buffers
        for camera_name, obs in synced_obs.items():
            if camera_name == self.main_camera:
                self.observation_buffers[camera_name].append(obs)
            else:
                if camera_name not in self.observation_buffers:
                    self.observation_buffers[camera_name] = deque([obs] * (self.model.model.obs_horizon - 1), 
                                                        maxlen=self.model.model.obs_horizon)
                self.observation_buffers[camera_name].append(obs)
        
    def run(self):
        """Diffusion Policy controller loop."""
        rate = rospy.Rate(50) # 150Hz control loop
        rate = None          
        self.home()
        i = 0
        start = time.time()
        while ((self.height is None or self.width is None) or (self.cartesian_pose_L is None or self.cartesian_pose_R is None) or time.time() - start < 5):
            self.home()
            if rate is not None:
                rate.sleep()
            self.solve_ik()
            self.update_visualization()
            
            super().publish_joint_commands()
            if i % 750 == 0:
                self.call_gripper(side = 'left', gripper_state = False, enable = True)
                rospy.sleep(0.2)
                self.call_gripper(side = 'right', gripper_state = False, enable = True)
                logger.info("Waiting for camera topic or robot pose data...")
                i = 0
            i += 1
        
        rospy.sleep(1.5)
        step = 0
        # output_dir = "/home/xi/yumi_realtime/debugging_output"
        self.last_action = None
        while not rospy.is_shutdown():
            assert len(self.proprio_buffer) == self.model.model.obs_horizon
            # Stack all camera observations
            all_camera_obs = []
            for camera_name in sorted(self.observation_buffers.keys()):  # Sort to ensure consistent order
                assert len(self.observation_buffers[camera_name]) == self.model.model.obs_horizon
                cam_obs = onp.array(self.observation_buffers[camera_name])
                all_camera_obs.append(cam_obs)
            
            # Stack along the N_C dimension
            stacked_obs = onp.stack(all_camera_obs, axis=1)  # [T, N_C, C, H, W]
            
            # CAMERA DEBUG
            # import matplotlib.pyplot as plt
            # plot_stacked_obs(stacked_obs)
            # import pdb; pdb.set_trace()
            self._update_proprio_queue_viz()
            input = {
            "observation": torch.from_numpy(stacked_obs).unsqueeze(0),  # [B, T, N_C, C, H, W]
            "proprio": torch.from_numpy(onp.array(self.proprio_buffer)).unsqueeze(0) # [B, T, D] 
                }
            
            start = time.time()
            step += 1

            if self.last_action is not None:
                # check gripper state of last action 
                target_left_gripper = self.last_action[9] < self.gripper_thres
                target_right_gripper = self.last_action[19] < self.gripper_thres

                current_left_gripper = input["proprio"][0, -1, 9] < self.gripper_thres
                current_right_gripper = input["proprio"][0, -1, 19] < self.gripper_thres
                
                print("current_left_gripper: ", current_left_gripper)

                # delta pose 
                target_proprio_left = self.last_action[:3]
                current_proprio_left = input["proprio"][0, -1, :3].numpy()
            
                # calculate lag 
                lag = onp.linalg.norm(target_proprio_left - current_proprio_left)
                print("lag: ", lag)

                # if they are in disgreemnt, gripper control with last action 
                if target_left_gripper != current_left_gripper or target_right_gripper != current_right_gripper:
                # if target_left_gripper != current_left_gripper or target_right_gripper != current_right_gripper or lag > 0.005:
                    print("blocking with last action")
                    self._yumi_control(self.last_action, rate)
                    continue

            # receding horizon control
            if self.control_mode == 'receding_horizon_control':
                if len(self.action_queue) > 0:
                    # self._update_action_queue_viz()
                    action = self.action_queue.popleft()
                    self._yumi_control(action, rate)
                    continue
            # end of receding horizon control
            
            action_prediction = self.model(input) # Denoise action prediction from obs and proprio...
            
            self.action_prediction = action_prediction
            self._update_action_queue_viz()

            action_L = action_prediction[0,:,:10]
            action_R = action_prediction[0,:,10:]
            
            action = onp.concatenate([action_L, action_R], axis=-1)
            
            # # temporal emsemble start
            if self.control_mode == 'temporal_ensemble':
                # import pdb; pdb.set_trace()
                new_actions = deque(action[:self.model.model.action_horizon])
                self.action_queue.append(new_actions)
                actions_current_timestep = onp.empty((len(self.action_queue), self.model.model.action_dim))
                
                k = 0.07
                for i, q in enumerate(self.action_queue):
                    actions_current_timestep[i] = q.popleft()
                    # self._update_action_queue_viz()
                exp_weights = onp.exp(k * onp.arange(actions_current_timestep.shape[0]))
                exp_weights = exp_weights / exp_weights.sum()
                # import pdb; pdb.set_trace()
                action = (actions_current_timestep * exp_weights[:, None]).sum(axis=0)
                self.temporal_ensemble_action = action
                # action[9] = action_L[0,-1]
                # action[19] = action_R[0,-1]
                
            # receding horizon # check the receding horizon block as well
            if self.control_mode == 'receding_horizon_control':
                if len(self.action_queue) == 0: 
                    self.action_queue = deque([a for a in action])
                action = self.action_queue.popleft()
            
            # update yumi action 
            self._yumi_control(action, rate)
            # self._update_action_queue_viz()
    
    def _yumi_control(self, action, rate = None):
        # YuMi action update
        ######################################################################
        self.last_action = action
        l_act = action_10d_to_8d(action[:10])
        r_act = action_10d_to_8d(action[10:])
        l_xyz, l_wxyz, l_gripper_cmd = l_act[:3], l_act[3:-1], l_act[-1]
        r_xyz, r_wxyz, r_gripper_cmd = r_act[:3], r_act[3:-1], r_act[-1]
        print("left xyz: ", l_xyz)
        print("left gripper: ", l_gripper_cmd)
        
        super().update_target_pose(
        side='left',
        position=l_xyz,
        wxyz=l_wxyz,
        gripper_state=bool(l_gripper_cmd<self.gripper_thres), 
        enable=True
        )
        
        super().update_target_pose(
        side='right',
        position=r_xyz,
        wxyz=r_wxyz,
        gripper_state=bool(r_gripper_cmd<self.gripper_thres), 
        enable=True
        )
        ######################################################################
        
        self.solve_ik()
        self.update_visualization()
        super().publish_joint_commands()
        
        if rate is not None:
            rate.sleep()
    
    def update_curr_proprio(self):
        l_xyz, l_xyzw = tf2xyz_quat(self.cartesian_pose_L)
        r_xyz, r_xyzw = tf2xyz_quat(self.cartesian_pose_R)
        
        l_q = Rotation.from_quat(l_xyzw)
        l_rot = l_q.as_matrix()
        l_rot_6d = onp.squeeze(rot_mat_to_rot_6d(l_rot[None]), axis=0)# [N, 6]
        r_q = Rotation.from_quat(r_xyzw)
        r_rot = r_q.as_matrix()
        r_rot_6d = onp.squeeze(rot_mat_to_rot_6d(r_rot[None]), axis=0) # [N, 6]
        
        self.cur_proprio = onp.concatenate([l_xyz, l_rot_6d, onp.array([int(self.gripper_L_pos)/10000]), r_xyz, r_rot_6d, onp.array([int(self.gripper_R_pos)/10000])], axis=-1, dtype=onp.float32)
        assert self.cur_proprio.shape == (20,)

        self.proprio_buffer.append(self.cur_proprio)

    def episode_start(self):
        """Reset the environment and start a new episode."""
        self.image_primary.clear()
        self.image_wrist.clear()
        self.prev_action.clear()
        self.proprio_buffer.clear()
        self.action_queue.clear()
        self.cur_proprio = None
        self.home() # Move to home position as first action
        rospy.sleep(5)
    
    def _setup_scene(self):
        # if self.control_mode == 'receding_horizon_control':
        while self.cartesian_pose_L is None or self.cartesian_pose_R is None:
            rospy.sleep(0.1)
        self.action_queue_viz_L = self.server.scene.add_point_cloud(
            name = "action_queue_L", 
            points = onp.array([[self.cartesian_pose_L.transform.translation.x,
                                self.cartesian_pose_L.transform.translation.y,
                                self.cartesian_pose_L.transform.translation.z]]), 
            colors = onp.array([[1.0, 0.0, 0.0]]), 
            point_size=0.005,
            point_shape='circle'
            )
        self.action_queue_viz_R = self.server.scene.add_point_cloud(
            name = "action_queue_R", 
            points = onp.array([[self.cartesian_pose_R.transform.translation.x,
                                self.cartesian_pose_R.transform.translation.y,
                                self.cartesian_pose_R.transform.translation.z]]), 
            colors = onp.array([[1.0, 0.0, 0.0]]), 
            point_size=0.005,
            point_shape='circle'
            )
        self.proprio_queue_viz_L = self.server.scene.add_point_cloud(
            name = "proprio_queue_L", 
            points = onp.array([[self.cartesian_pose_L.transform.translation.x,
                                self.cartesian_pose_L.transform.translation.y,
                                self.cartesian_pose_L.transform.translation.z]]), 
            colors = onp.array([[1.0, 0.0, 1.0]]), 
            point_size=0.007,
            )
        self.proprio_queue_viz_R = self.server.scene.add_point_cloud(
            name = "proprio_queue_R", 
            points = onp.array([[self.cartesian_pose_R.transform.translation.x,
                                self.cartesian_pose_R.transform.translation.y,
                                self.cartesian_pose_R.transform.translation.z]]), 
            colors = onp.array([[1.0, 0.0, 1.0]]), 
            point_size=0.007,
            )
            
    def _update_action_queue_viz(self):
        # import pdb; pdb.set_trace()
        # if self.control_mode == 'receding_horizon_control':
        #     action_queue_L = self.action_prediction[0,:,:3]
        #     action_queue_R = self.action_prediction[0,:,10:13]
        # elif self.control_mode == 'temporal_ensemble':
        #     if getattr(self, 'temporal_ensemble_action', None) is None:
        #         return
        #     action_queue_L = self.temporal_ensemble_action[:3]
        #     action_queue_R = self.temporal_ensemble_action[10:13]
        
        action_queue_L = self.action_prediction[0,:,:3]
        action_queue_R = self.action_prediction[0,:,10:13]
        self.action_queue_viz_L.points = action_queue_L
        color_order = onp.linspace(0.0, 1.0, len(action_queue_L))
        self.action_queue_viz_L.colors = onp.array([onp.array([c, 0.0, 0.0]) for c in color_order])
        self.action_queue_viz_R.points = action_queue_R
        self.action_queue_viz_R.colors = onp.array([onp.array([c, 0.0, 0.0]) for c in color_order])
    
    def _update_proprio_queue_viz(self):
        if len(self.proprio_buffer) > 0:
            proprio_queue_L = onp.array([a[:3] for a in onp.array(self.proprio_buffer)])
            proprio_queue_R = onp.array([a[10:13] for a in onp.array(self.proprio_buffer)])
            self.proprio_queue_viz_L.points = proprio_queue_L
            color_order = onp.linspace(0.0, 1.0, len(proprio_queue_L))
            self.proprio_queue_viz_L.colors = onp.array([onp.array([c, 0.0, 1.0]) for c in color_order])
            self.proprio_queue_viz_R.points = proprio_queue_R
            self.proprio_queue_viz_R.colors = onp.array([onp.array([c, 0.0, 1.0]) for c in color_order])
        
    def profile_run(self):
        profiler = LineProfiler()
        profiled_run = profiler(self.run)
        profiled_run()
        profiler.print_stats()

def plot_stacked_obs(stacked_obs):
    """
    Plot stacked observations from multiple cameras across time steps.
    
    Args:
        stacked_obs: numpy array of shape [T, N_C, C, H, W]
        T: number of timesteps
        N_C: number of cameras
        C: channels (3 for RGB)
        H, W: height and width
    """
    import matplotlib.pyplot as plt
    T, N_C, C, H, W = stacked_obs.shape
    
    # Create a grid of subplots
    fig, axes = plt.subplots(T, N_C, figsize=(4*N_C, 4*T))
    if T == 1 and N_C == 1:
        axes = np.array([[axes]])
    elif T == 1:
        axes = axes.reshape(1, -1)
    elif N_C == 1:
        axes = axes.reshape(-1, 1)
    
    # Plot each image
    for t in range(T):
        for nc in range(N_C):
            # Transform from [C, H, W] to [H, W, C] for plotting
            img = stacked_obs[t, nc].transpose(1, 2, 0)
            
            # Plot
            axes[t, nc].imshow(img)
            axes[t, nc].axis('off')
            axes[t, nc].set_title(f'Time {t}, Camera {nc}')
    
    plt.tight_layout()
    plt.show()
                
def main(
    # some signal 
    # ckpt_path : str = "/home/xi/checkpoints/241203_2002", 
    # ckpt_id: int = 99
    
    # Dec 4
    # ckpt_path : str = "/home/xi/checkpoints/241203_2104", 
    # ckpt_id : int = 299,

    # ckpt_path : str = "/home/xi/checkpoints/241203_217", 
    # ckpt_id : int = 299,

    # ckpt_path : str = "/home/xi/checkpoints/241203_2108", 
    # ckpt_id : int = 599,

    ckpt_path : str = "/home/xi/checkpoints/241205_1219",
    ckpt_id : int = 299,
    ): 
    
    yumi_interface = YuMiDiffusionPolicyController(ckpt_path, ckpt_id)
    yumi_interface.run()
    # yumi_interface.profile_run()
    
if __name__ == "__main__":
    tyro.cli(main)
