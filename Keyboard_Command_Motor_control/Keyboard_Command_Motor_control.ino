#include <micro_ros_arduino.h>
#include <Arduino.h>
#include <stdio.h>
#include <rcl/rcl.h>
#include <rclc/rclc.h>
#include <rcl/error_handling.h>
#include <rclc/executor.h>
#include <math.h>

#include <geometry_msgs/msg/twist.h>
#include <std_msgs/msg/int32_multi_array.h>
#include <std_msgs/msg/float32.h>
#include <std_msgs/msg/int32_multi_array.h>

rcl_allocator_t allocator;
rcl_subscription_t subscriber;
rcl_publisher_t publisher;
rcl_node_t node;
rcl_timer_t timer;
rclc_executor_t executor;
rclc_support_t support;


std_msgs__msg__Int32MultiArray encoder_msg;
std_msgs__msg__Int32MultiArray motor_msg;

// static const float wheel_radius = 0.021f;  // [m] 21mm
// static const float wheel_base = 0.185f;    // [m] 185mm
// static const int PPR = 48;                 // 48 PPR × 4X decode = 192 CPR
// static const float loop_hz = 50.0f;        // [Hz]
// static const float dt = 1.0f / loop_hz;

// Motor 1 (Right)
#define IN1 4
#define IN2 16
#define ENA 17
#define ENC_R_A 19
#define ENC_R_B 18

// Motor 2 (Left)
#define IN3 27
#define IN4 14
#define ENB 26
#define ENC_L_A 33
#define ENC_L_B 32



volatile long encodercount1 = 0;
volatile long encodercount2 = 0;


void IRAM_ATTR encoder1ISR()
{
  if(digitalRead(ENC_L_B) == HIGH)
  {
    encodercount1++;
  }
  else encodercount1--;
}


void IRAM_ATTR encoder2ISR()
{
  if(digitalRead(ENC_R_B) == HIGH)
  {
    encodercount2++;
  }
  else encodercount2--;
}


void publish_data_callback(rcl_timer_t *timer, int64_t last_call_time) {
  (void)last_call_time;
  if (timer != NULL) {
    encoder_msg.data.data[0] = encodercount1;
    encoder_msg.data.data[1] = encodercount2;
    rcl_publish(&publisher, &encoder_msg, NULL);
  }
}


void motor_pwm_callback(const void *msgin)
{
  const std_msgs__msg__Int32MultiArray *msg = (const std_msgs__msg__Int32MultiArray *) msgin;
  int pwm_L = msg->data.data[0];
  int pwm_R = msg->data.data[1];
  int direction = msg->data.data[2];

  if(direction == 1)
  {
    analogWrite(ENA, pwm_R);
    analogWrite(ENB, pwm_L);
    forward();
  }
  else if(direction == -1)
  {
    analogWrite(ENA, pwm_R);
    analogWrite(ENB,pwm_L);
    backward();
  }
}




void setup() {
  Serial.begin(115200);
  set_microros_transports();
  
  pinMode(IN1, OUTPUT);
  pinMode(IN2, OUTPUT);
  pinMode(ENA, OUTPUT);
  pinMode(IN3, OUTPUT);
  pinMode(IN4, OUTPUT);
  pinMode(ENB, OUTPUT);

  pinMode(ENC_L_A, INPUT_PULLUP);
  pinMode(ENC_L_B, INPUT_PULLUP);
  pinMode(ENC_R_A, INPUT_PULLUP);
  pinMode(ENC_R_B, INPUT_PULLUP);

  attachInterrupt(digitalPinToInterrupt(ENC_L_A), encoder1ISR, RISING);
  attachInterrupt(digitalPinToInterrupt(ENC_R_A), encoder2ISR, RISING);


  allocator = rcl_get_default_allocator();

  rclc_support_init(&support,0,NULL, &allocator);
  rclc_node_init_default(&node, "micro_ros_esp32_node", "", &support);

  rclc_subscription_init_default(&subscriber, &node,
   ROSIDL_GET_MSG_TYPE_SUPPORT(std_msgs, msg, Int32MultiArray), "/get_pwm_values");

  motor_msg.data.size = 3;
  motor_msg.data.capacity = 3;
  motor_msg.data.data = (int32_t*)malloc(2*sizeof(size_t));

  rclc_publisher_init_default(&publisher, &node,
    ROSIDL_GET_MSG_TYPE_SUPPORT(std_msgs, msg, Int32MultiArray), "/get_ticks");

  rclc_timer_init_default(&timer, &support, RCL_MS_TO_NS(50), publish_data_callback);

  encoder_msg.data.size = 2;
  encoder_msg.data.capacity = 2;
  encoder_msg.data.data = (int32_t*)malloc(2 * sizeof(int32_t));
  encoder_msg.data.data[0] = 0.0;
  encoder_msg.data.data[1] = 0.0;

  rclc_executor_init(&executor, &support.context, 2, &allocator);
  rclc_executor_add_timer(&executor, &timer);
  rclc_executor_add_subscription(&executor, &subscriber, &motor_msg, motor_pwm_callback, ON_NEW_DATA);
  // rclc_executor_add_subscription(&executor, &subscriber, &motor_msg, pid_output_callback, ON_NEW_DATA);

  // put your setup code here, to run once:
}

void loop() {
  rclc_executor_spin_some(&executor, RCL_MS_TO_NS(10));
  delay(1);
  // put your main code here, to run repeatedly:

}
