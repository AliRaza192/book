---
sidebar_position: 3
title: "Chapter 2: ROS 2 Core Concepts - Nodes, Topics, and Services"
description: "Exploring the fundamental building blocks of ROS 2: nodes for computation, topics for asynchronous communication, and services for synchronous requests."
keywords: [ROS 2, nodes, topics, services, publish-subscribe, request-response]
learningObjectives:
  - Define and understand ROS 2 nodes
  - Explain the publish-subscribe pattern with topics
  - Understand request-response communication with services
  - Compare different communication paradigms in ROS 2
---

# Chapter 2: ROS 2 Core Concepts - Nodes, Topics, and Services

## Nodes: The Building Blocks of ROS 2

In ROS 2, a **node** is an executable process that performs computation. Nodes are the fundamental building blocks of any ROS 2 system, representing individual software components that perform specific functions within the robot system.

Think of nodes as specialized workers in a factory. Each node has a specific job - one might process camera images, another might control motors, and another might plan paths. These nodes work together to achieve the robot's overall goals.

### Characteristics of Nodes

- **Process-based**: Each node runs as a separate process, providing isolation between components
- **Specialized**: Each node typically focuses on a specific task or capability
- **Communicative**: Nodes communicate with other nodes through topics, services, and other mechanisms
- **Identifiable**: Each node has a unique name within the ROS 2 system

Nodes can be written in different programming languages (C++, Python, Rust, etc.) and still communicate seamlessly through ROS 2's communication infrastructure.

## Topics: Publish-Subscribe Communication

**Topics** enable asynchronous, one-way communication between nodes using a publish-subscribe pattern. This communication model is ideal for streaming data like sensor readings, robot state information, or commands that multiple nodes might need simultaneously.

### How Topics Work

In the publish-subscribe pattern:
- **Publishers** send messages to a topic
- **Subscribers** receive messages from a topic
- Multiple publishers can send to the same topic
- Multiple subscribers can receive from the same topic
- Publishers and subscribers don't need to know about each other

### Real-World Analogy

Think of topics like radio stations. A radio station (publisher) broadcasts music to the airwaves (topic), and anyone with a radio (subscriber) tuned to that frequency can receive the broadcast. Multiple people can listen to the same station simultaneously, and the station doesn't know who's listening.

### Common Use Cases for Topics

- Sensor data streams (camera images, LiDAR scans, IMU readings)
- Robot state information (position, velocity, battery levels)
- Motion commands (velocity commands, joint positions)
- Event notifications (obstacle detected, goal reached)

## Services: Request-Response Communication

**Services** enable synchronous, two-way communication between nodes using a request-response pattern. This model is ideal for operations that require immediate responses or when one node needs to request specific information or actions from another.

### How Services Work

In the request-response pattern:
- A **client** sends a request to a service
- A **server** receives the request, processes it, and sends back a response
- The client waits for the response before continuing
- There's typically one server for each service (though advanced configurations exist)

### Real-World Analogy

Think of services like a customer service desk. You (the client) walk up and make a specific request (like asking for information), and the customer service representative (the server) processes your request and gives you a response. You wait for the response before leaving.

### Common Use Cases for Services

- Map loading or saving
- Dynamic parameter configuration
- Transform lookup (finding spatial relationships)
- Specific action requests (take photo, calibrate sensor)

## Comparing Communication Paradigms

### Topics vs Services

| Aspect | Topics | Services |
|--------|--------|----------|
| Communication Style | Asynchronous | Synchronous |
| Data Direction | One-way (publish/subscribe) | Two-way (request/response) |
| Timing | Continuous streaming | On-demand |
| Coupling | Loose (publishers/subscribers don't know each other) | Tight (client/server must know each other) |
| Use Case | Streaming data, broadcasting | Specific requests, immediate responses |

### When to Use Each

- Use **topics** for continuous data streams, broadcasting information to multiple recipients, or when the sender doesn't need confirmation of receipt
- Use **services** for specific requests that require immediate responses, configuration changes, or when you need guaranteed delivery and processing

## Practical Example: Mobile Robot

Consider a mobile robot navigating through a building:

- **Nodes**: Navigation node, sensor processing node, motor control node, mapping node
- **Topics**:
  - `/camera/image_raw` - Camera images published by sensor node, subscribed by perception node
  - `/cmd_vel` - Velocity commands published by navigation node, subscribed by motor control node
  - `/scan` - Laser scan data published by sensor node, subscribed by multiple nodes
- **Services**:
  - `/save_map` - Service to save the current map when requested
  - `/set_parameters` - Service to dynamically configure parameters

## Summary

Nodes, topics, and services form the core communication infrastructure of ROS 2. Understanding these concepts is crucial for designing effective robotic systems. Nodes provide the computational building blocks, topics enable efficient data streaming through publish-subscribe, and services provide reliable request-response communication for specific interactions.

In the next chapter, we'll explore how Python-based AI agents connect to ROS 2 systems using the rclpy client library.