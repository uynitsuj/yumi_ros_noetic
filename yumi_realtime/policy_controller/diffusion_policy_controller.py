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
        self.height = None
        self.width = None
        # if 'image_sub' not in self.__dict__.keys():
        self.image_sub = rospy.Subscriber('/camera/image_raw', Image, self.image_callback)
        
        self.proprio_buffer = deque([],maxlen=self.model.model.obs_horizon)
        self.image_primary, self.image_wrist = deque([],maxlen=self.model.model.obs_horizon), deque([],maxlen=self.model.model.obs_horizon)
        self.action_queue = deque([],maxlen=self.model.model.action_horizon//2)
        self.prev_action = deque([],maxlen=self.model.model.obs_horizon)
        self.cur_proprio = None
        
        self.cartesian_pose_L = None
        self.cartesian_pose_R = None
        
        self.control_mode = 'receeding_horizon_control'
        # self.control_mode = 'temporal_ensemble'
        
        self.bridge = CvBridge()
        
        logger.info("Diffusion Policy controller initialized")

        self.gripper_thres = 0.014
    
    def run(self):
        """Diffusion Policy controller loop."""
        rate = rospy.Rate(15) # 150Hz control loop          
        self.home()
        i = 0
        while ((self.height is None or self.width is None) or (self.cartesian_pose_L is None or self.cartesian_pose_R is None)):
            self.home()
            rate.sleep()
            self.solve_ik()
            self.update_visualization()
            
            super().publish_joint_commands()
            if i % 750 == 0:
                self.call_gripper(side = 'left', gripper_state = False, enable = True)
                self.call_gripper(side = 'right', gripper_state = False, enable = True)
                logger.info("Waiting for camera topic or robot pose data...")
                i = 0
            i += 1
        
        rospy.sleep(1.5)
        step = 0
        output_dir = "/home/xi/yumi_realtime/debugging_output"
        self.last_action = None
        while not rospy.is_shutdown():
            input = {
            "observation": torch.from_numpy(onp.array(self.image_primary)).unsqueeze(0).unsqueeze(2), # [B, T, C, N_C, H, W]
            "proprio": torch.from_numpy(onp.array(self.proprio_buffer)).unsqueeze(0) # [B, T, D] 
                }
                    
            start = time.time()
            print("current step: ", step)
            step += 1
            print("current proprio left: ", input["proprio"][0, -1, :3])
            print("current gripper left: ", input["proprio"][0, -1, 9])

            if self.last_action is not None:
                # check gripper state of last action 
                target_left_gripper = self.last_action[9] < self.gripper_thres
                target_right_gripper = self.last_action[19] < self.gripper_thres

                current_left_gripper = input["proprio"][0, -1, 9] < self.gripper_thres
                current_right_gripper = input["proprio"][0, -1, 19] < self.gripper_thres

                # delta pose 
                target_proprio_left = self.last_action[:3]
                current_proprio_left = input["proprio"][0, -1, :3].numpy()
            
                # calculate lag 
                lag = onp.linalg.norm(target_proprio_left - current_proprio_left)
                print("lag: ", lag)

                # if they are in disgreemnt, gripper control with last action 
                if target_left_gripper != current_left_gripper or target_right_gripper != current_right_gripper:
                # if target_left_gripper != current_left_gripper or target_right_gripper != current_right_gripper or lag > 0.005:
                    self._yumi_control(self.last_action, rate)
                    continue

            # receeding horizon control
            if self.control_mode == 'receeding_horizon_control':
                if len(self.action_queue) > 0:
                    action = self.action_queue.popleft()
                    self._yumi_control(action, rate)
                    continue
            # end of receeding horizon control
                
            action_prediction = self.model(input) # Denoise action prediction from obs and proprio...

            action_L = action_prediction[0,:,:10]
            action_R = action_prediction[0,:,10:]
            
            action = onp.concatenate([action_L, action_R], axis=-1)
                        
            # # temporal emsemble start
            if self.control_mode == 'temporal_ensemble':
                new_actions = deque(action[:self.model.model.action_horizon])
                self.action_queue.append(new_actions)
                actions_current_timestep = onp.empty((len(self.action_queue), self.model.model.action_dim*2))
                
                k = 0.02
                for i, q in enumerate(self.action_queue):
                    actions_current_timestep[i] = q.popleft()
                exp_weights = onp.exp(k * onp.arange(actions_current_timestep.shape[0]))
                exp_weights = exp_weights / exp_weights.sum()
                action = (actions_current_timestep * exp_weights[:, None]).sum(axis=0)
                action[9] = action_L[-1,-1]
                action[19] = action_R[-1,-1]
                
            # receeding horizon # check the receeding horizon block as well
            if self.control_mode == 'receeding_horizon_control':
                if len(self.action_queue) == 0: 
                    self.action_queue = deque([a for a in action])
                action = self.action_queue.popleft()
            
            # update yumi action 
            self._yumi_control(action, rate)
    
    def _yumi_control(self, action, rate):
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
    
    def image_callback(self, image_msg: Image):

        """Handle camera observation updates."""
        if self.height is None and self.width is None:
            self.height = image_msg.height
            self.width = image_msg.width
            logger.info(f"First image received; Observation dim: {self.height}x{self.width}x3")
        
        onp_img = self.bridge.imgmsg_to_cv2(image_msg, desired_encoding='rgb8').astype("float32") / 255.0  # H, W, C
        
        new_obs = onp.transpose(onp_img, (2, 0, 1)) # C, H, W
        
        if self.cartesian_pose_L is None or self.cartesian_pose_R is None:
            return
        
        while len(self.image_primary) < self.model.model.obs_horizon - 1:
            self.image_primary.append(new_obs)
            self.update_curr_proprio()

        self.image_primary.append(new_obs)
        self.update_curr_proprio()
        
        # Ensure both buffers are full at this point
        assert len(self.image_primary) == self.model.model.obs_horizon
        assert len(self.proprio_buffer) == self.model.model.obs_horizon
              
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
        
    def plot_action_queue(self, side: Literal['left', 'right'] = None, color: Tuple = (255,0,0), size: int = 5):
        """Plot the action queue for the given side."""
        
        for i, action in enumerate(self.action_queue):
            if side == 'left':
                self.plot_action(action[:10], color, size)
            elif side == 'right':
                self.plot_action(action[10:], color, size)
            
    
def main(
    # some signal 
    # ckpt_path : str = "/home/xi/checkpoints/241203_2002", 
    # ckpt_id: int = 99
    
    # Dec 4
    # ckpt_path : str = "/home/xi/checkpoints/241203_2104", 
    # ckpt_id : int = 299,

    # ckpt_path : str = "/home/xi/checkpoints/241203_217", 
    # ckpt_id : int = 299,

    ckpt_path : str = "/home/xi/checkpoints/241203_2108", 
    ckpt_id : int = 599,
    ): 
    
    yumi_interface = YuMiDiffusionPolicyController(ckpt_path, ckpt_id)
    yumi_interface.run()
    
if __name__ == "__main__":
    tyro.cli(main)
