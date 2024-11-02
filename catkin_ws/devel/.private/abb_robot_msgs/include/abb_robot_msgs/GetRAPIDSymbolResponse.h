// Generated by gencpp from file abb_robot_msgs/GetRAPIDSymbolResponse.msg
// DO NOT EDIT!


#ifndef ABB_ROBOT_MSGS_MESSAGE_GETRAPIDSYMBOLRESPONSE_H
#define ABB_ROBOT_MSGS_MESSAGE_GETRAPIDSYMBOLRESPONSE_H


#include <string>
#include <vector>
#include <memory>

#include <ros/types.h>
#include <ros/serialization.h>
#include <ros/builtin_message_traits.h>
#include <ros/message_operations.h>


namespace abb_robot_msgs
{
template <class ContainerAllocator>
struct GetRAPIDSymbolResponse_
{
  typedef GetRAPIDSymbolResponse_<ContainerAllocator> Type;

  GetRAPIDSymbolResponse_()
    : value()
    , result_code(0)
    , message()  {
    }
  GetRAPIDSymbolResponse_(const ContainerAllocator& _alloc)
    : value(_alloc)
    , result_code(0)
    , message(_alloc)  {
  (void)_alloc;
    }



   typedef std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>> _value_type;
  _value_type value;

   typedef uint16_t _result_code_type;
  _result_code_type result_code;

   typedef std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>> _message_type;
  _message_type message;





  typedef boost::shared_ptr< ::abb_robot_msgs::GetRAPIDSymbolResponse_<ContainerAllocator> > Ptr;
  typedef boost::shared_ptr< ::abb_robot_msgs::GetRAPIDSymbolResponse_<ContainerAllocator> const> ConstPtr;

}; // struct GetRAPIDSymbolResponse_

typedef ::abb_robot_msgs::GetRAPIDSymbolResponse_<std::allocator<void> > GetRAPIDSymbolResponse;

typedef boost::shared_ptr< ::abb_robot_msgs::GetRAPIDSymbolResponse > GetRAPIDSymbolResponsePtr;
typedef boost::shared_ptr< ::abb_robot_msgs::GetRAPIDSymbolResponse const> GetRAPIDSymbolResponseConstPtr;

// constants requiring out of line definition



template<typename ContainerAllocator>
std::ostream& operator<<(std::ostream& s, const ::abb_robot_msgs::GetRAPIDSymbolResponse_<ContainerAllocator> & v)
{
ros::message_operations::Printer< ::abb_robot_msgs::GetRAPIDSymbolResponse_<ContainerAllocator> >::stream(s, "", v);
return s;
}


template<typename ContainerAllocator1, typename ContainerAllocator2>
bool operator==(const ::abb_robot_msgs::GetRAPIDSymbolResponse_<ContainerAllocator1> & lhs, const ::abb_robot_msgs::GetRAPIDSymbolResponse_<ContainerAllocator2> & rhs)
{
  return lhs.value == rhs.value &&
    lhs.result_code == rhs.result_code &&
    lhs.message == rhs.message;
}

template<typename ContainerAllocator1, typename ContainerAllocator2>
bool operator!=(const ::abb_robot_msgs::GetRAPIDSymbolResponse_<ContainerAllocator1> & lhs, const ::abb_robot_msgs::GetRAPIDSymbolResponse_<ContainerAllocator2> & rhs)
{
  return !(lhs == rhs);
}


} // namespace abb_robot_msgs

namespace ros
{
namespace message_traits
{





template <class ContainerAllocator>
struct IsMessage< ::abb_robot_msgs::GetRAPIDSymbolResponse_<ContainerAllocator> >
  : TrueType
  { };

template <class ContainerAllocator>
struct IsMessage< ::abb_robot_msgs::GetRAPIDSymbolResponse_<ContainerAllocator> const>
  : TrueType
  { };

template <class ContainerAllocator>
struct IsFixedSize< ::abb_robot_msgs::GetRAPIDSymbolResponse_<ContainerAllocator> >
  : FalseType
  { };

template <class ContainerAllocator>
struct IsFixedSize< ::abb_robot_msgs::GetRAPIDSymbolResponse_<ContainerAllocator> const>
  : FalseType
  { };

template <class ContainerAllocator>
struct HasHeader< ::abb_robot_msgs::GetRAPIDSymbolResponse_<ContainerAllocator> >
  : FalseType
  { };

template <class ContainerAllocator>
struct HasHeader< ::abb_robot_msgs::GetRAPIDSymbolResponse_<ContainerAllocator> const>
  : FalseType
  { };


template<class ContainerAllocator>
struct MD5Sum< ::abb_robot_msgs::GetRAPIDSymbolResponse_<ContainerAllocator> >
{
  static const char* value()
  {
    return "2e935abf84f6e652529bba09693d1ffe";
  }

  static const char* value(const ::abb_robot_msgs::GetRAPIDSymbolResponse_<ContainerAllocator>&) { return value(); }
  static const uint64_t static_value1 = 0x2e935abf84f6e652ULL;
  static const uint64_t static_value2 = 0x529bba09693d1ffeULL;
};

template<class ContainerAllocator>
struct DataType< ::abb_robot_msgs::GetRAPIDSymbolResponse_<ContainerAllocator> >
{
  static const char* value()
  {
    return "abb_robot_msgs/GetRAPIDSymbolResponse";
  }

  static const char* value(const ::abb_robot_msgs::GetRAPIDSymbolResponse_<ContainerAllocator>&) { return value(); }
};

template<class ContainerAllocator>
struct Definition< ::abb_robot_msgs::GetRAPIDSymbolResponse_<ContainerAllocator> >
{
  static const char* value()
  {
    return "\n"
"#-------------------------------------------------------------------------------\n"
"# Service response fields\n"
"#-------------------------------------------------------------------------------\n"
"# Value (in raw text format) of the RAPID symbol.\n"
"string value\n"
"\n"
"# Service success/failure indicator.\n"
"# Refer to 'abb_robot_msgs/ServiceResponses' for defined error codes.\n"
"uint16 result_code\n"
"\n"
"# Status message (empty if service succeeded).\n"
"string message\n"
"\n"
;
  }

  static const char* value(const ::abb_robot_msgs::GetRAPIDSymbolResponse_<ContainerAllocator>&) { return value(); }
};

} // namespace message_traits
} // namespace ros

namespace ros
{
namespace serialization
{

  template<class ContainerAllocator> struct Serializer< ::abb_robot_msgs::GetRAPIDSymbolResponse_<ContainerAllocator> >
  {
    template<typename Stream, typename T> inline static void allInOne(Stream& stream, T m)
    {
      stream.next(m.value);
      stream.next(m.result_code);
      stream.next(m.message);
    }

    ROS_DECLARE_ALLINONE_SERIALIZER
  }; // struct GetRAPIDSymbolResponse_

} // namespace serialization
} // namespace ros

namespace ros
{
namespace message_operations
{

template<class ContainerAllocator>
struct Printer< ::abb_robot_msgs::GetRAPIDSymbolResponse_<ContainerAllocator> >
{
  template<typename Stream> static void stream(Stream& s, const std::string& indent, const ::abb_robot_msgs::GetRAPIDSymbolResponse_<ContainerAllocator>& v)
  {
    s << indent << "value: ";
    Printer<std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>>>::stream(s, indent + "  ", v.value);
    s << indent << "result_code: ";
    Printer<uint16_t>::stream(s, indent + "  ", v.result_code);
    s << indent << "message: ";
    Printer<std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>>>::stream(s, indent + "  ", v.message);
  }
};

} // namespace message_operations
} // namespace ros

#endif // ABB_ROBOT_MSGS_MESSAGE_GETRAPIDSYMBOLRESPONSE_H
