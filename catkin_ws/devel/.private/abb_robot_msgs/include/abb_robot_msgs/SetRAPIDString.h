// Generated by gencpp from file abb_robot_msgs/SetRAPIDString.msg
// DO NOT EDIT!


#ifndef ABB_ROBOT_MSGS_MESSAGE_SETRAPIDSTRING_H
#define ABB_ROBOT_MSGS_MESSAGE_SETRAPIDSTRING_H

#include <ros/service_traits.h>


#include <abb_robot_msgs/SetRAPIDStringRequest.h>
#include <abb_robot_msgs/SetRAPIDStringResponse.h>


namespace abb_robot_msgs
{

struct SetRAPIDString
{

typedef SetRAPIDStringRequest Request;
typedef SetRAPIDStringResponse Response;
Request request;
Response response;

typedef Request RequestType;
typedef Response ResponseType;

}; // struct SetRAPIDString
} // namespace abb_robot_msgs


namespace ros
{
namespace service_traits
{


template<>
struct MD5Sum< ::abb_robot_msgs::SetRAPIDString > {
  static const char* value()
  {
    return "ca1f63f0ec40ce75b501bc490a118a6c";
  }

  static const char* value(const ::abb_robot_msgs::SetRAPIDString&) { return value(); }
};

template<>
struct DataType< ::abb_robot_msgs::SetRAPIDString > {
  static const char* value()
  {
    return "abb_robot_msgs/SetRAPIDString";
  }

  static const char* value(const ::abb_robot_msgs::SetRAPIDString&) { return value(); }
};


// service_traits::MD5Sum< ::abb_robot_msgs::SetRAPIDStringRequest> should match
// service_traits::MD5Sum< ::abb_robot_msgs::SetRAPIDString >
template<>
struct MD5Sum< ::abb_robot_msgs::SetRAPIDStringRequest>
{
  static const char* value()
  {
    return MD5Sum< ::abb_robot_msgs::SetRAPIDString >::value();
  }
  static const char* value(const ::abb_robot_msgs::SetRAPIDStringRequest&)
  {
    return value();
  }
};

// service_traits::DataType< ::abb_robot_msgs::SetRAPIDStringRequest> should match
// service_traits::DataType< ::abb_robot_msgs::SetRAPIDString >
template<>
struct DataType< ::abb_robot_msgs::SetRAPIDStringRequest>
{
  static const char* value()
  {
    return DataType< ::abb_robot_msgs::SetRAPIDString >::value();
  }
  static const char* value(const ::abb_robot_msgs::SetRAPIDStringRequest&)
  {
    return value();
  }
};

// service_traits::MD5Sum< ::abb_robot_msgs::SetRAPIDStringResponse> should match
// service_traits::MD5Sum< ::abb_robot_msgs::SetRAPIDString >
template<>
struct MD5Sum< ::abb_robot_msgs::SetRAPIDStringResponse>
{
  static const char* value()
  {
    return MD5Sum< ::abb_robot_msgs::SetRAPIDString >::value();
  }
  static const char* value(const ::abb_robot_msgs::SetRAPIDStringResponse&)
  {
    return value();
  }
};

// service_traits::DataType< ::abb_robot_msgs::SetRAPIDStringResponse> should match
// service_traits::DataType< ::abb_robot_msgs::SetRAPIDString >
template<>
struct DataType< ::abb_robot_msgs::SetRAPIDStringResponse>
{
  static const char* value()
  {
    return DataType< ::abb_robot_msgs::SetRAPIDString >::value();
  }
  static const char* value(const ::abb_robot_msgs::SetRAPIDStringResponse&)
  {
    return value();
  }
};

} // namespace service_traits
} // namespace ros

#endif // ABB_ROBOT_MSGS_MESSAGE_SETRAPIDSTRING_H
