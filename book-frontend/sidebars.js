// @ts-check

// This runs in Node.js - Don't use client-side code here (browser APIs, JSX...)

/**
 * Creating a sidebar enables you to:
 - create an ordered group of docs
 - render a sidebar for each doc of that group
 - provide next/previous navigation

 The sidebars can be generated from the filesystem, or explicitly defined here.

 Create as many sidebars as you want.

 @type {import('@docusaurus/plugin-content-docs').SidebarsConfig}
 */
const sidebars = {
  // By default, Docusaurus generates a sidebar from the docs folder structure
  tutorialSidebar: [
    {
      type: 'category',
      label: '🤖 Module 1 – The Robotic Nervous System (ROS 2)',
      items: [
        {
          type: 'doc',
          id: 'ros2-course-module/introduction-to-ros2',
          label: 'Chapter 1: Introduction to ROS 2 and Middleware for Robots',
        },
        {
          type: 'doc',
          id: 'ros2-course-module/nodes-topics-services',
          label: 'Chapter 2: ROS 2 Core Concepts - Nodes, Topics, and Services',
        },
        {
          type: 'doc',
          id: 'ros2-course-module/python-agents-with-rclpy',
          label: 'Chapter 3: Bridging Python AI Agents to Robots using rclpy',
        },
        {
          type: 'doc',
          id: 'ros2-course-module/humanoid-urdf-basics',
          label: 'Chapter 4: Understanding Humanoid Structure with URDF',
        },
      ],
    },
    {
      type: 'category',
      label: '🎮 Module 2 – The Digital Twin (Gazebo & Unity)',
      items: [
        {
          type: 'doc',
          id: 'digital-twin-simulation/digital-twins-overview',
          label: 'Chapter 1: Digital Twins Overview',
        },
        {
          type: 'doc',
          id: 'digital-twin-simulation/physics-simulation-gazebo',
          label: 'Chapter 2: Physics Simulation with Gazebo',
        },
        {
          type: 'doc',
          id: 'digital-twin-simulation/virtual-environments-unity',
          label: 'Chapter 3: Virtual Environments with Unity',
        },
        {
          type: 'doc',
          id: 'digital-twin-simulation/sensor-simulation',
          label: 'Chapter 4: Chapter 4 Heading',
        },
      ],
    },
    {
      type: 'category',
      label: '🧠 Module 3 – The AI-Robot Brain (NVIDIA Isaac™)',
      items: [
        {
          type: 'doc',
          id: 'nvidia-isaac-ai-robot/nvidia-isaac-overview',
          label: 'Chapter 1: Introduction to NVIDIA Isaac and AI-Driven Robotics',
        },
        {
          type: 'doc',
          id: 'nvidia-isaac-ai-robot/isaac-sim-synthetic-data',
          label: 'Chapter 2: Isaac Sim: Photorealistic Simulation and Synthetic Data',
        },
        {
          type: 'doc',
          id: 'nvidia-isaac-ai-robot/isaac-ros-vslam',
          label: 'Chapter 3: Isaac ROS: Accelerated Perception and VSLAM',
        },
        {
          type: 'doc',
          id: 'nvidia-isaac-ai-robot/nav2-humanoid-navigation',
          label: 'Chapter 4: Nav2 for Humanoid Navigation and Path Planning',
        },
      ],
    },
    {
      type: 'category',
      label: '💬 Module 4 – Vision-Language-Action (VLA)',
      items: [
        {
          type: 'doc',
          id: 'module-4/vla-overview',
          label: 'Chapter 1: Vision-Language-Action (VLA) Overview',
        },
        {
          type: 'doc',
          id: 'module-4/voice-to-action',
          label: 'Chapter 2: Voice-to-Action Systems',
        },
        {
          type: 'doc',
          id: 'module-4/llm-cognitive-planning',
          label: 'Chapter 3: LLM Cognitive Planning',
        },
        {
          type: 'doc',
          id: 'module-4/capstone-autonomous-humanoid',
          label: 'Chapter 4: Capstone - Autonomous Humanoid Robot',
        },
      ],
    },
  ],

  // But you can create a sidebar manually
  /*
  tutorialSidebar: [
    'intro',
    'hello',
    {
      type: 'category',
      label: 'Tutorial',
      items: ['tutorial-basics/create-a-document'],
    },
  ],
   */
};

export default sidebars;
