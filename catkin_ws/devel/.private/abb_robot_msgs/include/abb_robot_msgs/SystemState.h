// Generated by gencpp from file abb_robot_msgs/SystemState.msg
// DO NOT EDIT!


#ifndef ABB_ROBOT_MSGS_MESSAGE_SYSTEMSTATE_H
#define ABB_ROBOT_MSGS_MESSAGE_SYSTEMSTATE_H


#include <string>
#include <vector>
#include <memory>

#include <ros/types.h>
#include <ros/serialization.h>
#include <ros/builtin_message_traits.h>
#include <ros/message_operations.h>

#include <std_msgs/Header.h>
#include <abb_robot_msgs/RAPIDTaskState.h>
#include <abb_robot_msgs/MechanicalUnitState.h>

namespace abb_robot_msgs
{
template <class ContainerAllocator>
struct SystemState_
{
  typedef SystemState_<ContainerAllocator> Type;

  SystemState_()
    : header()
    , motors_on(false)
    , auto_mode(false)
    , rapid_running(false)
    , rapid_tasks()
    , mechanical_units()  {
    }
  SystemState_(const ContainerAllocator& _alloc)
    : header(_alloc)
    , motors_on(false)
    , auto_mode(false)
    , rapid_running(false)
    , rapid_tasks(_alloc)
    , mechanical_units(_alloc)  {
  (void)_alloc;
    }



   typedef  ::std_msgs::Header_<ContainerAllocator>  _header_type;
  _header_type header;

   typedef uint8_t _motors_on_type;
  _motors_on_type motors_on;

   typedef uint8_t _auto_mode_type;
  _auto_mode_type auto_mode;

   typedef uint8_t _rapid_running_type;
  _rapid_running_type rapid_running;

   typedef std::vector< ::abb_robot_msgs::RAPIDTaskState_<ContainerAllocator> , typename std::allocator_traits<ContainerAllocator>::template rebind_alloc< ::abb_robot_msgs::RAPIDTaskState_<ContainerAllocator> >> _rapid_tasks_type;
  _rapid_tasks_type rapid_tasks;

   typedef std::vector< ::abb_robot_msgs::MechanicalUnitState_<ContainerAllocator> , typename std::allocator_traits<ContainerAllocator>::template rebind_alloc< ::abb_robot_msgs::MechanicalUnitState_<ContainerAllocator> >> _mechanical_units_type;
  _mechanical_units_type mechanical_units;





  typedef boost::shared_ptr< ::abb_robot_msgs::SystemState_<ContainerAllocator> > Ptr;
  typedef boost::shared_ptr< ::abb_robot_msgs::SystemState_<ContainerAllocator> const> ConstPtr;

}; // struct SystemState_

typedef ::abb_robot_msgs::SystemState_<std::allocator<void> > SystemState;

typedef boost::shared_ptr< ::abb_robot_msgs::SystemState > SystemStatePtr;
typedef boost::shared_ptr< ::abb_robot_msgs::SystemState const> SystemStateConstPtr;

// constants requiring out of line definition



template<typename ContainerAllocator>
std::ostream& operator<<(std::ostream& s, const ::abb_robot_msgs::SystemState_<ContainerAllocator> & v)
{
ros::message_operations::Printer< ::abb_robot_msgs::SystemState_<ContainerAllocator> >::stream(s, "", v);
return s;
}


template<typename ContainerAllocator1, typename ContainerAllocator2>
bool operator==(const ::abb_robot_msgs::SystemState_<ContainerAllocator1> & lhs, const ::abb_robot_msgs::SystemState_<ContainerAllocator2> & rhs)
{
  return lhs.header == rhs.header &&
    lhs.motors_on == rhs.motors_on &&
    lhs.auto_mode == rhs.auto_mode &&
    lhs.rapid_running == rhs.rapid_running &&
    lhs.rapid_tasks == rhs.rapid_tasks &&
    lhs.mechanical_units == rhs.mechanical_units;
}

template<typename ContainerAllocator1, typename ContainerAllocator2>
bool operator!=(const ::abb_robot_msgs::SystemState_<ContainerAllocator1> & lhs, const ::abb_robot_msgs::SystemState_<ContainerAllocator2> & rhs)
{
  return !(lhs == rhs);
}


} // namespace abb_robot_msgs

namespace ros
{
namespace message_traits
{





template <class ContainerAllocator>
struct IsMessage< ::abb_robot_msgs::SystemState_<ContainerAllocator> >
  : TrueType
  { };

template <class ContainerAllocator>
struct IsMessage< ::abb_robot_msgs::SystemState_<ContainerAllocator> const>
  : TrueType
  { };

template <class ContainerAllocator>
struct IsFixedSize< ::abb_robot_msgs::SystemState_<ContainerAllocator> >
  : FalseType
  { };

template <class ContainerAllocator>
struct IsFixedSize< ::abb_robot_msgs::SystemState_<ContainerAllocator> const>
  : FalseType
  { };

template <class ContainerAllocator>
struct HasHeader< ::abb_robot_msgs::SystemState_<ContainerAllocator> >
  : TrueType
  { };

template <class ContainerAllocator>
struct HasHeader< ::abb_robot_msgs::SystemState_<ContainerAllocator> const>
  : TrueType
  { };


template<class ContainerAllocator>
struct MD5Sum< ::abb_robot_msgs::SystemState_<ContainerAllocator> >
{
  static const char* value()
  {
    return "46309669ed6ba4863375b03174d00ad7";
  }

  static const char* value(const ::abb_robot_msgs::SystemState_<ContainerAllocator>&) { return value(); }
  static const uint64_t static_value1 = 0x46309669ed6ba486ULL;
  static const uint64_t static_value2 = 0x3375b03174d00ad7ULL;
};

template<class ContainerAllocator>
struct DataType< ::abb_robot_msgs::SystemState_<ContainerAllocator> >
{
  static const char* value()
  {
    return "abb_robot_msgs/SystemState";
  }

  static const char* value(const ::abb_robot_msgs::SystemState_<ContainerAllocator>&) { return value(); }
};

template<class ContainerAllocator>
struct Definition< ::abb_robot_msgs::SystemState_<ContainerAllocator> >
{
  static const char* value()
  {
    return "#-------------------------------------------------------------------------------\n"
"# Description:\n"
"#   The purpose of this message definition, is to represent a subset of states\n"
"#   of an ABB robot controller system.\n"
"#-------------------------------------------------------------------------------\n"
"\n"
"#-------------------------------------------------------------------------------\n"
"# Message fields\n"
"#-------------------------------------------------------------------------------\n"
"# Metadata.\n"
"std_msgs/Header header\n"
"\n"
"# Motors on/off indicator.\n"
"bool motors_on\n"
"\n"
"# Auto/manual mode indicator.\n"
"bool auto_mode\n"
"\n"
"# RAPID running/stopped indicator.\n"
"bool rapid_running\n"
"\n"
"# RAPID task states.\n"
"RAPIDTaskState[] rapid_tasks\n"
"\n"
"# Mechanical unit states.\n"
"MechanicalUnitState[] mechanical_units\n"
"\n"
"================================================================================\n"
"MSG: std_msgs/Header\n"
"# Standard metadata for higher-level stamped data types.\n"
"# This is generally used to communicate timestamped data \n"
"# in a particular coordinate frame.\n"
"# \n"
"# sequence ID: consecutively increasing ID \n"
"uint32 seq\n"
"#Two-integer timestamp that is expressed as:\n"
"# * stamp.sec: seconds (stamp_secs) since epoch (in Python the variable is called 'secs')\n"
"# * stamp.nsec: nanoseconds since stamp_secs (in Python the variable is called 'nsecs')\n"
"# time-handling sugar is provided by the client library\n"
"time stamp\n"
"#Frame this data is associated with\n"
"string frame_id\n"
"\n"
"================================================================================\n"
"MSG: abb_robot_msgs/RAPIDTaskState\n"
"#-------------------------------------------------------------------------------\n"
"# Description:\n"
"#   The purpose of this message definition, is to represent a subset of states\n"
"#   of a RAPID task defined in an ABB robot controller system.\n"
"#-------------------------------------------------------------------------------\n"
"\n"
"#-------------------------------------------------------------------------------\n"
"# Enumerations\n"
"#-------------------------------------------------------------------------------\n"
"# RAPID execution states:\n"
"uint8 EXECUTION_STATE_UNKNOWN       = 1\n"
"uint8 EXECUTION_STATE_READY         = 2\n"
"uint8 EXECUTION_STATE_STOPPED       = 3\n"
"uint8 EXECUTION_STATE_STARTED       = 4\n"
"uint8 EXECUTION_STATE_UNINITIALIZED = 5\n"
"\n"
"#-------------------------------------------------------------------------------\n"
"# Message fields\n"
"#-------------------------------------------------------------------------------\n"
"# The RAPID task's name.\n"
"string name\n"
"\n"
"# The RAPID task's activated/deactivated status.\n"
"bool activated\n"
"\n"
"# The RAPID task's execution state.\n"
"uint8 execution_state\n"
"\n"
"# The RAPID task is a motion task.\n"
"bool motion_task\n"
"\n"
"================================================================================\n"
"MSG: abb_robot_msgs/MechanicalUnitState\n"
"#-------------------------------------------------------------------------------\n"
"# Description:\n"
"#   The purpose of this message definition, is to represent a subset of states\n"
"#   of a mechanical unit defined in an ABB robot controller system.\n"
"#-------------------------------------------------------------------------------\n"
"\n"
"#-------------------------------------------------------------------------------\n"
"# Message fields\n"
"#-------------------------------------------------------------------------------\n"
"# The mechanical unit's name.\n"
"string name\n"
"\n"
"# The mechanical unit's activated/deactivated status.\n"
"bool activated\n"
;
  }

  static const char* value(const ::abb_robot_msgs::SystemState_<ContainerAllocator>&) { return value(); }
};

} // namespace message_traits
} // namespace ros

namespace ros
{
namespace serialization
{

  template<class ContainerAllocator> struct Serializer< ::abb_robot_msgs::SystemState_<ContainerAllocator> >
  {
    template<typename Stream, typename T> inline static void allInOne(Stream& stream, T m)
    {
      stream.next(m.header);
      stream.next(m.motors_on);
      stream.next(m.auto_mode);
      stream.next(m.rapid_running);
      stream.next(m.rapid_tasks);
      stream.next(m.mechanical_units);
    }

    ROS_DECLARE_ALLINONE_SERIALIZER
  }; // struct SystemState_

} // namespace serialization
} // namespace ros

namespace ros
{
namespace message_operations
{

template<class ContainerAllocator>
struct Printer< ::abb_robot_msgs::SystemState_<ContainerAllocator> >
{
  template<typename Stream> static void stream(Stream& s, const std::string& indent, const ::abb_robot_msgs::SystemState_<ContainerAllocator>& v)
  {
    s << indent << "header: ";
    s << std::endl;
    Printer< ::std_msgs::Header_<ContainerAllocator> >::stream(s, indent + "  ", v.header);
    s << indent << "motors_on: ";
    Printer<uint8_t>::stream(s, indent + "  ", v.motors_on);
    s << indent << "auto_mode: ";
    Printer<uint8_t>::stream(s, indent + "  ", v.auto_mode);
    s << indent << "rapid_running: ";
    Printer<uint8_t>::stream(s, indent + "  ", v.rapid_running);
    s << indent << "rapid_tasks[]" << std::endl;
    for (size_t i = 0; i < v.rapid_tasks.size(); ++i)
    {
      s << indent << "  rapid_tasks[" << i << "]: ";
      s << std::endl;
      s << indent;
      Printer< ::abb_robot_msgs::RAPIDTaskState_<ContainerAllocator> >::stream(s, indent + "    ", v.rapid_tasks[i]);
    }
    s << indent << "mechanical_units[]" << std::endl;
    for (size_t i = 0; i < v.mechanical_units.size(); ++i)
    {
      s << indent << "  mechanical_units[" << i << "]: ";
      s << std::endl;
      s << indent;
      Printer< ::abb_robot_msgs::MechanicalUnitState_<ContainerAllocator> >::stream(s, indent + "    ", v.mechanical_units[i]);
    }
  }
};

} // namespace message_operations
} // namespace ros

#endif // ABB_ROBOT_MSGS_MESSAGE_SYSTEMSTATE_H
