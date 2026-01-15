---
title: "Terminology Glossary"
sidebar_position: -1
description: "Consistent terminology definitions across all modules in the Physical AI & Humanoid Robotics course"
---

# Terminology Glossary

## Common Terms Across All Modules

### Robot Intelligence
- **Definition**: The ability of robotic systems to perceive, reason, and act autonomously in response to environmental stimuli
- **Module Context**: Used in Module 1 (ROS 2 as the nervous system), Module 2 (simulation for intelligent behavior), and Module 3 (AI-driven autonomy)

### Perception
- **Definition**: The process by which robots acquire and interpret sensory information from their environment
- **Module Context**: Introduced in Module 1 (sensor nodes), expanded in Module 2 (sensor simulation), and advanced in Module 3 (accelerated perception)

### Navigation
- **Definition**: The capability of a robot to plan and execute paths from one location to another
- **Module Context**: Concept introduced in Module 1 (basic movement), simulated in Module 2 (virtual navigation), and realized in Module 3 (real-world navigation)

### Localization
- **Definition**: The process of determining a robot's position and orientation within its environment
- **Module Context**: Covered in Module 1 (coordinate frames), Module 2 (simulated localization), and Module 3 (real-time localization)

### SLAM (Simultaneous Localization and Mapping)
- **Definition**: The computational problem of constructing or updating a map of an unknown environment while simultaneously keeping track of an agent's location within it
- **Module Context**: Introduced in Module 1 (mapping concepts), simulated in Module 2 (virtual mapping), and implemented in Module 3 (VSLAM with Isaac ROS)

## Module 3 Specific Terms

### Isaac Ecosystem
- **Definition**: NVIDIA's integrated platform for developing and deploying AI-powered robots, comprising Isaac Sim, Isaac ROS, and Isaac Apps

### Isaac Sim
- **Definition**: NVIDIA's robotics simulator that combines NVIDIA Omniverse for photorealistic rendering with PhysX for accurate physics simulation

### Isaac ROS
- **Definition**: NVIDIA's collection of hardware-accelerated perception and navigation packages for ROS 2, leveraging GPU computing for enhanced performance

### VSLAM (Visual Simultaneous Localization and Mapping)
- **Definition**: A variant of SLAM that uses visual sensors (cameras) as the primary input for mapping and localization

### Synthetic Data
- **Definition**: Artificially generated data that mimics real-world observations, used to train AI models without requiring actual sensor data

### Humanoid Navigation
- **Definition**: Navigation systems specifically designed for bipedal robots, accounting for balance, gait patterns, and footstep planning

### Footstep Planning
- **Definition**: The process of determining where and when a humanoid robot should place its feet to maintain stability while navigating

### Bipedal Locomotion
- **Definition**: Two-legged walking motion, characteristic of humanoid robots and humans

### Balance Control
- **Definition**: The control systems that maintain a humanoid robot's stability during static and dynamic activities

### Center of Mass (COM)
- **Definition**: The point in a robot where the total mass is considered concentrated, critical for stability analysis

### Zero Moment Point (ZMP)
- **Definition**: A concept used in bipedal locomotion to indicate the point on the ground where the net moment of the ground reaction forces is zero

### Behavior Trees
- **Definition**: A mathematical model of plan execution used in robotics to structure the execution of tasks in a logical manner

### Nav2 (Navigation2)
- **Definition**: The next-generation navigation framework for ROS 2, providing improved architecture and capabilities for mobile robot navigation

### Gait Patterns
- **Definition**: The specific rhythmic patterns of limb movements that characterize different types of locomotion

### Traversability Analysis
- **Definition**: The process of evaluating terrain characteristics to determine whether a robot can safely navigate through it

### Multi-Modal Navigation
- **Definition**: Navigation systems capable of switching between different modes of locomotion (walking, climbing, crawling, etc.)

### Model Predictive Control (MPC)
- **Definition**: An advanced control method that uses a model of the system to predict future behavior and optimize control actions

### Inverse Kinematics (IK)
- **Definition**: The mathematical process of determining joint angles required to achieve a desired end-effector position

### Terrain Adaptation
- **Definition**: The capability of a robot to modify its behavior based on the characteristics of the surface it is navigating

### Sim-to-Real Transfer
- **Definition**: The process of transferring skills, behaviors, or models trained in simulation to real-world robotic systems

### Hardware Acceleration
- **Definition**: The use of specialized hardware (like GPUs) to speed up computation-intensive tasks, particularly in perception and AI inference