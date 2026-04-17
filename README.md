<p align="center">
  <a href="https://ztfr.eu/matrix">
    <img src="assets/community-badge.png" alt="Join Zeitfresser Matrix Community" height="70" />
  </a>
</p>

<h1 align="center">
GTS-Federator
</span>
<h4 align="center">
<span style="display:inline-flex; align-items:center; gap:12px;">
A powerful RSS-based discovery engine to populate GoToSocial instances.
</span>
<p>

<h6 align="center">
  <a href="https://ztfr.eu">🏰 Website</a>
  ·
  <a href="https://ztfr.eu/matrix">📰 Zeitfresser Matrix Community</a>
  ·
  <a href="https://social.ztfr.eu/@federator">🐘 Fediverse</a> 
  ·
  <a href="https://look.ztfr.eu/#/#support:ztfr.eu">💬 Supportchat</a> 
</h6>
<br>

## ✨ Introduction

**GTS-Federator** is a high-efficiency content discovery tool designed for [GoToSocial](https://codeberg.org/superseriousbusiness/gotosocial) instances. It solves the "empty timeline" problem of small or personal instances by automatically discovering and federating content from RSS feeds across the Fediverse.

By leveraging RSS feeds from larger instances or specific hashtags, GTS-Federator acts as a lightweight alternative to traditional relays, giving you full control over what kind of content populates your federated timeline.

This project is a refined and modernized fork of the original [HolMirDas](https://github.com/aliceif/HolMirDas) concepts, specifically optimized for Docker deployment, long-term stability, and GoToSocial's unique architecture.

## 🛠 What this bot is for

GTS-Federator is not a relay in the traditional sense. It is a targeted discovery engine. Instead of receiving everything from a relay, you "pull" exactly what interests you.

It is a perfect fit if you:

- run a personal or small GoToSocial instance (especially on low-power hardware like a Synology NAS or Raspberry Pi)
- want to populate your federated timeline with specific topics (via Hashtag-RSS)
- prefer a pull-based discovery over the "firehose" of public relays
- need a "set and forget" solution that runs silently in the background

## 🚀 Core Features

### Smart Content Discovery
The bot monitors a configurable list of RSS feeds. For every new entry found, it triggers your GoToSocial instance to fetch and federate the post. This makes the content available for your local users and populates your instance's database with new remote profiles and statuses.

### Efficient Resource Management
Unlike many other fetchers, GTS-Federator is designed with a "Single User" philosophy. It uses a persistent HTTP session and a local JSON-based memory to ensure that your instance isn't hammered with redundant requests.

### Real-Time Analytics
After every run, the bot provides a clean summary of its activity:
- **Runtime:** How long the discovery took.
- **New Posts:** Number of successfully federated statuses.
- **Instance Growth:** Tracking how many new Fediverse domains your instance has discovered through the process.

### Adaptive Pausing & Timezone Support
The bot calculates its next run based on your local time. With built-in timezone support, the logs will always show you exactly when the next discovery cycle starts, matching your local wall clock.

### Production-Ready Dockerization
The entire application is container-native. It runs as a non-root user for enhanced security and can be deployed in seconds using Docker Compose.

## 🧠 Design Philosophy

GTS-Federator follows a few key principles:

- **Keep it lightweight** – Written in clean Python, utilizing minimal RAM and CPU.
- **Zero-Maintenance** – Once configured, it handles rate limits, connection timeouts, and state persistence automatically.
- **Privacy First** – No external tracking. The bot only communicates with your instance and the RSS sources you define.
- **Transparency** – Clear, human-readable logs that tell you exactly what is happening.

## ⚙️ Configuration

Configuration is handled primarily via environment variables in your `.env` file.

| Variable | Description | Default |
| :--- | :--- | :--- |
| `GTS_SERVER_URL` | Your GoToSocial Instance URL | - |
| `GTS_ACCESS_TOKEN` | Your App Access Token | - |
| `FETCH_INTERVAL` | Time between runs (e.g., `30m`, `1h`) | `30m` |
| `MAX_POSTS_PER_RUN` | Max posts to fetch per feed per run | `25` |
| `TZ` | Your Timezone (e.g., `Europe/Berlin`) | `UTC` |

## 📦 Installation

### Preparation

Before deploying, you need to set up the directory structure. This ensures the bot can save its "memory" and find your configuration.

1. Create the Project Folder: Create a main directory (e.g., gts-federation).
2. Create the Data Subfolder: Inside that folder, create a subfolder named data. This is where the bot stores its database (processed_urls.json).
3. Place your Files: Put your compose.yaml, .env, and rss_feeds.txt into the main directory.

### Folder Structure:

Your final structure should look like this:

```

gts-federation/
├── data/               <-- Subfolder for the database (Required)
├── .env                <-- Your credentials & settings
├── compose.yaml        <-- Docker configuration
└── rss_feeds.txt       <-- Your list of RSS feeds

```

### Note on Permissions: 

Ensure the data folder is writable. If you are using a specific UID (e.g., on a Synology NAS), assign ownership to that user: `chown -R 1026:100 ./data`

### Compose.yaml

```
version: "3"

services:
  gts-federation:
    image: domoel/gts-federator:latest
    container_name: gts-federator
    #user: 1026:100 # If you run into permission issues with the 'data' folder, make sure to set the correct UID/GID for your system.
    volumes:
      - ./data:/app/data
      - ./rss_feeds.txt:/app/rss_feeds.txt:ro
    environment:
      - TZ=Europe/Berlin # Change to your local timezone.
    env_file:
      - .env
    restart: always
```
