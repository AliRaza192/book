import clsx from 'clsx';
import Link from '@docusaurus/Link';
import useDocusaurusContext from '@docusaurus/useDocusaurusContext';
import Layout from '@theme/Layout';
import Heading from '@theme/Heading';
import styles from './index.module.css';

function HomepageHeader() {
  const {siteConfig} = useDocusaurusContext();
  return (
    <header className={clsx(styles.heroBanner)}>
      <div className="container">
        <div className={styles.heroContainer}>
          <Heading as="h1" className={clsx(styles.heroTitle)}>
            {siteConfig.title}
          </Heading>
          <p className={clsx(styles.heroSubtitle)}>
            {siteConfig.tagline}
          </p>
          <div className={clsx(styles.buttonGroup)}>
            <Link
              className="button button--primary button--lg"
              to="/docs/intro">
              Start Reading
            </Link>
            <Link
              className="button button--secondary button--lg"
              to="/docs/intro">
              View Modules
            </Link>
          </div>
        </div>
      </div>
    </header>
  );
}

const modules = [
  {
    emoji: '🤖',
    title: 'Module 1 – The Robotic Nervous System (ROS 2)',
    description: 'Master ROS 2 fundamentals, nodes, topics, and services',
    link: '/docs/ros2-course-module/introduction-to-ros2',
  },
  {
    emoji: '🎮',
    title: 'Module 2 – The Digital Twin (Gazebo & Unity)',
    description: 'Build realistic simulations with physics engines',
    link: '/docs/digital-twin-simulation/digital-twins-overview',
  },
  {
    emoji: '🧠',
    title: 'Module 3 – The AI-Robot Brain (NVIDIA Isaac™)',
    description: 'Implement AI-driven robotics with NVIDIA Isaac',
    link: '/docs/nvidia-isaac-ai-robot/nvidia-isaac-overview',
  },
  {
    emoji: '💬',
    title: 'Module 4 – Vision-Language-Action (VLA)',
    description: 'Create autonomous systems with voice and vision',
    link: '/docs/module-4/vla-overview',
  },
];

function ModuleCards() {
  return (
    <section className="modules-section">
      <div className="modules-container">
        <div className="modules-grid">
          {modules.map((module, idx) => (
            <Link
              key={idx}
              to={module.link}
              className="module-card">
              <span className="module-card-emoji">{module.emoji}</span>
              <h3 className="module-card-title">{module.title}</h3>
              <p className="module-card-description">{module.description}</p>
              <span className="module-card-arrow">Explore module</span>
            </Link>
          ))}
        </div>
      </div>
    </section>
  );
}

export default function Home() {
  const {siteConfig} = useDocusaurusContext();
  return (
    <Layout
      title={`Home - ${siteConfig.title}`}
      description="Mastering AI-Driven Robotics with NVIDIA Isaac, ROS 2, and Advanced Simulation Techniques">
      <HomepageHeader />
      <main>
        <ModuleCards />
      </main>
    </Layout>
  );
}
