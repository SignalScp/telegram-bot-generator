# Changelog

All notable changes to the Telegram Bot Generator project will be documented in this file.

## [2.0.0] - 2024-12-23

### Major Changes
- **New:** JSON database system (`database.py`) for storing bot metadata locally
- **Removed:** API key requirement for OnlySq API (using free tier)
- **Updated:** All modules to use JSON database instead of SQLite
- **Improved:** Configuration system for local database

### Added
- `database.py` - Full JSON database manager with CRUD operations
- Database statistics and analytics
- Per-user bot tracking
- Bot status history in database
- `/stats` command for database statistics
- Database backup and export functionality
- Database import from backup files
- Fallback responses for OnlySq API failures
- Better error handling for database operations

### Changed
- `config.py` - Removed `ONLYSQ_API_KEY` requirement
- `onlysq_client.py` - No longer requires API authentication
- `bot_generator.py` - Updated to use `user_id` for database tracking
- `main.py` - Integrated JSON database for all bot operations
- `.env.example` - Simplified, only requires Telegram bot token
- Documentation updated to reflect no API key requirement

### Database Structure
```json
{
  "metadata": {
    "version": "1.0",
    "created_at": "ISO timestamp",
    "updated_at": "ISO timestamp"
  },
  "bots": {
    "bot_id": {
      "bot_id": "unique identifier",
      "name": "bot name",
      "description": "bot description",
      "user_id": "telegram user id",
      "status": "running/stopped/error",
      "code_file": "path to bot code",
      "code_length": "bytes",
      "created_at": "ISO timestamp",
      "updated_at": "ISO timestamp"
    }
  }
}
```

### Database Operations Supported
- Add bot
- Get bot by ID
- Get all bots
- Update bot
- Delete bot
- Filter by status
- Filter by user
- Get statistics
- Export/import bots
- Create backups

### Benefits of Version 2.0

✅ **No API Key Needed** - Completely free, instant access to OnlySq models

✅ **Local Database** - All data stored on your PC in JSON format

✅ **Better Privacy** - No data sent to external services

✅ **Easier Setup** - Only need Telegram bot token

✅ **More Control** - Edit database directly if needed

✅ **Simple Backups** - Just copy the JSON file

✅ **User Isolation** - Each user has their own bots tracked

✅ **Offline Capable** - Database operations work offline

### Migration from 1.0

If upgrading from 1.0:
1. Backup any existing SQLite database
2. Pull latest version
3. Delete old database files
4. Run `python main.py`
5. New JSON database will be created automatically

### Files Changed
- config.py (updated)
- onlysq_client.py (updated)
- bot_generator.py (updated)
- main.py (updated)
- .env.example (updated)
- database.py (new)
- README.md (updated)
- INSTALLATION.md (updated)

## [1.0.0] - 2024-12-23

### Initial Release
- AI-powered bot code generation using OnlySq API
- Telegram bot interface with `/generate` command
- Bot process execution and lifecycle management
- Bot templates with base and enhanced options
- Code generation with AI (system and user prompts)
- Code validation and security checks
- Bot management commands (`/list`, `/status`, `/stop`)
- Configuration via environment variables
- Logging and error handling
- Complete documentation

### Features
- Generate Telegram bots from natural language descriptions
- Deploy generated bots as separate processes
- Manage multiple bots simultaneously
- Monitor bot status in real-time
- Code templates for quick generation
- Security checks for generated code
- OnlySq API integration (OpenAI compatible)

### Documentation Included
- README.md - Project overview
- INSTALLATION.md - Setup guide
- USAGE.md - Usage examples
- PROJECT_SUMMARY.md - Architecture overview
- LICENSE - MIT license

### Technology Stack
- Python 3.8+
- python-telegram-bot 21.1
- OnlySq API (40+ models)
- httpx for HTTP requests
- python-dotenv for configuration

---

## Development Notes

### Version 2.1 (Planned)
- [ ] Web dashboard for bot management
- [ ] Advanced analytics
- [ ] Bot versioning and rollback
- [ ] Scheduled bot tasks
- [ ] Bot monetization framework

### Version 2.2 (Planned)
- [ ] Multi-language bot generation
- [ ] Bot templates marketplace
- [ ] Docker containerization
- [ ] Kubernetes support
- [ ] Advanced code generation with tree search

## Compatibility

### Python Versions
- ✅ Python 3.8
- ✅ Python 3.9
- ✅ Python 3.10
- ✅ Python 3.11
- ✅ Python 3.12

### Operating Systems
- ✅ Windows 10+
- ✅ macOS 10.14+
- ✅ Linux (Ubuntu, Debian, etc.)

## Known Issues

### Version 2.0.0
- None reported

### Version 1.0.0
- Requires API key for OnlySq (fixed in 2.0)
- SQLite database adds complexity (fixed in 2.0)

## Contributing

Contributions welcome! Areas:
- Bug fixes
- Feature suggestions
- Documentation improvements
- Code optimization
- Test coverage
- Example bots

## Support

For issues or questions:
1. Check documentation first
2. Search existing GitHub issues
3. Create new GitHub issue with:
   - Python version
   - Operating system
   - Error message
   - Steps to reproduce

---

**Last Updated:** December 23, 2024

**Maintainer:** SignalScp
