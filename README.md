# GTS-HolMirDas 🚀

RSS-based content discovery for [GoToSocial](https://codeberg.org/superseriousbusiness/gotosocial) instances.

Automatically discovers and federates content from RSS feeds across the Fediverse, helping small GoToSocial instances populate their federated timeline without relying on traditional relays.

Inspired by the original [HolMirDas](https://github.com/aliceif/HolMirDas) by [@aliceif](https://mkultra.x27.one/@aliceif), adapted for GoToSocial with enhanced Docker deployment and multi-instance processing.

## ✨ Key Features

- **📡 Multi-Instance Discovery** - Fetches content from configurable RSS feeds across Fediverse instances
- **⚡ Performance Scaling** - 20-100 posts per feed with URL parameters (`?limit=100`)  
- **🐳 Production Ready** - Docker deployment, environment-based config, health monitoring
- **📊 Comprehensive Stats** - Runtime metrics, federation growth, performance tracking
- **🔧 Zero Maintenance** - Runs automatically every hour with duplicate detection

## 🚀 Quick Start

```bash
# Clone the repository
git clone https://git.klein.ruhr/matthias/gts-holmirdas
cd gts-holmirdas

# Copy configuration templates
cp .env.example .env
cp rss_feeds.example.txt rss_feeds.txt

# Edit configuration
nano .env              # Add your GTS credentials
nano rss_feeds.txt     # Customize RSS feeds

# Deploy
docker compose up -d

# Monitor
docker compose logs -f
```

## 📈 Performance at Scale

**Real Production Data:**
```
📊 Runtime: 8:42 | 487 posts processed | 3,150+ instances discovered
⚡ 56 posts/minute | 102 RSS feeds | +45 new instances per run
💾 Resource usage: ~450MB RAM total (GoToSocial + tools)
```

**Scaling Options:**
- **Conservative:** 20 posts/feed (~100 posts/run)
- **Balanced:** 50 posts/feed (~300 posts/run) 
- **Aggressive:** 100 posts/feed (~600 posts/run)

## 🛠️ Configuration Essentials

### Environment Variables (.env)
```bash
# Required
GTS_SERVER_URL=https://your-gts-instance.tld
GTS_ACCESS_TOKEN=your_gts_access_token

# Performance Tuning
MAX_POSTS_PER_RUN=25              # Posts per feed per run
DELAY_BETWEEN_REQUESTS=1          # Seconds between API calls
LOG_LEVEL=INFO                    # DEBUG for troubleshooting
```

### RSS Feeds (rss_feeds.txt)
```bash
# Use URL parameters to scale performance
https://mastodon.social/tags/homelab.rss?limit=50
https://fosstodon.org/tags/selfhosting.rss?limit=100
https://infosec.exchange/tags/security.rss?limit=75
```

### GoToSocial Access Token
1. Login to your GoToSocial instance
2. Settings → Applications → Create new application
3. Required scopes: `read`, `read:search`, `read:statuses`
4. Copy access token to `.env` file

## 📖 Complete Documentation

For detailed information, visit our **[Wiki](https://git.klein.ruhr/matthias/gts-holmirdas/wiki)**:

- **[📋 Installation Guide](https://git.klein.ruhr/matthias/gts-holmirdas/wiki/Installation-Guide.-)** - Detailed setup, Docker configuration, deployment options
- **[📈 Performance & Scaling](https://git.klein.ruhr/matthias/gts-holmirdas/wiki/Performance-%26-Scaling)** - Optimization tables, scaling strategies, resource planning  
- **[🛠️ Troubleshooting](https://git.klein.ruhr/matthias/gts-holmirdas/wiki/Troubleshooting)** - Common issues, Docker problems, debugging guide
- **[⚙️ Advanced Configuration](https://git.klein.ruhr/matthias/gts-holmirdas/wiki/Advanced-Configuration)** - Environment variables, RSS strategies, production tips
- **[📊 Monitoring & Stats](https://git.klein.ruhr/matthias/gts-holmirdas/wiki/Monitoring-%26-Stats)** - Understanding output, health monitoring, metrics
- **[❓ FAQ](https://git.klein.ruhr/matthias/gts-holmirdas/wiki/FAQ+-+Frequently+Asked+Questions.-)** - Common questions and answers

## 🤝 Community & Support

- **[Contributing Guide](Contributing)** - Development setup and contribution guidelines *(coming soon)*
- **Issues**: [Report bugs or request features](https://git.klein.ruhr/matthias/gts-holmirdas/issues)  
- **Contact**: [@matthias@me.klein.ruhr](https://me.klein.ruhr/@matthias) on the Fediverse

## 🔗 Related Projects

- **[FediFetcher](https://github.com/nanos/fedifetcher)** - Fetches missing replies and posts
- **[GoToSocial](https://github.com/superseriousbusiness/gotosocial)** - Lightweight ActivityPub server  
- **[slurp](https://github.com/VyrCossont/slurp)** - Import posts from other instances

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Inspired by [HolMirDas](https://github.com/aliceif/HolMirDas) by [@aliceif](https://mkultra.x27.one/@aliceif)
- Built for the GoToSocial community
- RSS-to-ActivityPub federation approach