// Dashboard JavaScript
class Dashboard {
    constructor() {
        this.currentUser = null;
        this.guilds = [];
        this.currentSection = 'overview';
        this.init();
    }

    async init() {
        await this.checkAuth();
        this.setupNavigation();
        this.setupEventListeners();
        this.loadDashboardData();
    }

    async checkAuth() {
        try {
            const response = await fetch('/auth/check');
            const data = await response.json();
            
            if (!data.authenticated) {
                window.location.href = '/login';
                return;
            }

            const userResponse = await fetch('/auth/user');
            this.currentUser = await userResponse.json();
            this.updateUserInfo();
        } catch (error) {
            console.error('Auth check failed:', error);
            window.location.href = '/login';
        }
    }

    updateUserInfo() {
        const avatar = document.getElementById('user-avatar');
        const name = document.getElementById('user-name');
        
        if (this.currentUser.avatar) {
            avatar.src = `https://cdn.discordapp.com/avatars/${this.currentUser.id}/${this.currentUser.avatar}.png`;
        } else {
            avatar.src = `https://cdn.discordapp.com/embed/avatars/${this.currentUser.discriminator % 5}.png`;
        }
        
        name.textContent = this.currentUser.username;
    }

    setupNavigation() {
        const navItems = document.querySelectorAll('.nav-item');
        navItems.forEach(item => {
            item.addEventListener('click', () => {
                const section = item.dataset.section;
                this.switchSection(section);
            });
        });
    }

    switchSection(sectionName) {
        // Update nav active state
        document.querySelectorAll('.nav-item').forEach(item => {
            item.classList.remove('active');
        });
        document.querySelector(`[data-section="${sectionName}"]`).classList.add('active');

        // Update content visibility
        document.querySelectorAll('.content-section').forEach(section => {
            section.classList.remove('active');
        });
        document.getElementById(sectionName).classList.add('active');

        this.currentSection = sectionName;
        this.loadSectionData(sectionName);
    }

    loadSectionData(sectionName) {
        switch(sectionName) {
            case 'overview':
                this.loadOverviewData();
                break;
            case 'music':
                this.loadMusicData();
                break;
            case 'moderation':
                this.loadModerationData();
                break;
            case 'tempvoice':
                this.loadTempVoiceData();
                break;
            case 'custom':
                this.loadCustomCommandsData();
                break;
            case 'settings':
                this.loadSettingsData();
                break;
        }
    }

    async loadDashboardData() {
        try {
            // Load bot status
            const statusResponse = await fetch('/api/bot/status');
            const statusData = await statusResponse.json();
            this.updateBotStatus(statusData);

            // Load user guilds
            const guildsResponse = await fetch('/api/user/guilds');
            const guildsData = await guildsResponse.json();
            this.guilds = guildsData.guilds;
            this.renderGuilds();
        } catch (error) {
            console.error('Error loading dashboard data:', error);
        }
    }

    updateBotStatus(data) {
        document.getElementById('total-servers').textContent = data.guilds || 0;
        document.getElementById('total-users').textContent = data.users || 0;
        document.getElementById('bot-status').textContent = data.status || 'Offline';
    }

    renderGuilds() {
        const container = document.getElementById('guilds-container');
        
        if (this.guilds.length === 0) {
            container.innerHTML = '<p>Tidak ada server yang tersedia</p>';
            return;
        }

        container.innerHTML = this.guilds.map(guild => `
            <div class="guild-item">
                <img class="guild-icon" src="${guild.icon_url || 'https://cdn.discordapp.com/embed/avatars/0.png'}" 
                     alt="${guild.name}">
                <div class="guild-name">${guild.name}</div>
                <div class="guild-members">${guild.member_count} members</div>
                <button class="btn btn-primary" onclick="selectGuild('${guild.id}')">
                    <i class="fas fa-cog"></i> Manage
                </button>
            </div>
        `).join('');
    }

    async loadMusicData() {
        // Populate server select for music
        const select = document.getElementById('music-server-select');
        select.innerHTML = '<option value="">Pilih server...</option>';
        
        this.guilds.forEach(guild => {
            select.innerHTML += `<option value="${guild.id}">${guild.name}</option>`;
        });
    }

    async loadTempVoiceData() {
        // Populate server select for tempvoice
        const select = document.getElementById('tempvoice-server-select');
        select.innerHTML = '<option value="">Pilih server...</option>';
        
        this.guilds.forEach(guild => {
            select.innerHTML += `<option value="${guild.id}">${guild.name}</option>`;
        });
    }

    async loadCustomCommandsData() {
        try {
            const response = await fetch('/api/commands');
            const data = await response.json();
            this.renderCustomCommands(data.commands);
        } catch (error) {
            console.error('Error loading custom commands:', error);
        }
    }

    renderCustomCommands(commands) {
        const container = document.getElementById('custom-commands-list');
        const customCommands = commands.filter(cmd => cmd.type === 'custom');
        
        if (customCommands.length === 0) {
            container.innerHTML = '<p>Belum ada custom commands</p>';
            return;
        }

        container.innerHTML = customCommands.map(cmd => `
            <div class="command-item">
                <div class="command-name">${cmd.name}</div>
                <div class="command-description">${cmd.description}</div>
                <button class="btn btn-danger" onclick="deleteCommand('${cmd.name}')">
                    <i class="fas fa-trash"></i>
                </button>
            </div>
        `).join('');
    }

    setupEventListeners() {
        // Music controls
        document.getElementById('music-server-select').addEventListener('change', (e) => {
            this.selectMusicServer(e.target.value);
        });

        // TempVoice controls
        document.getElementById('tempvoice-server-select').addEventListener('change', (e) => {
            this.selectTempVoiceServer(e.target.value);
        });

        // Volume control
        document.getElementById('volume-slider').addEventListener('input', (e) => {
            this.updateVolume(e.target.value);
        });
    }

    async selectMusicServer(guildId) {
        if (!guildId) return;
        
        try {
            const response = await fetch(`/api/music/${guildId}`);
            const data = await response.json();
            this.updateMusicDisplay(data);
        } catch (error) {
            console.error('Error loading music data:', error);
        }
    }

    updateMusicDisplay(data) {
        document.getElementById('current-title').textContent = data.currentTrack?.title || 'Tidak ada lagu yang diputar';
        document.getElementById('current-artist').textContent = data.currentTrack?.artist || '-';
        
        if (data.currentTrack?.thumbnail) {
            document.getElementById('current-thumbnail').src = data.currentTrack.thumbnail;
        }
    }

    async musicAction(action) {
        const guildId = document.getElementById('music-server-select').value;
        if (!guildId) {
            alert('Pilih server terlebih dahulu');
            return;
        }

        try {
            const response = await fetch(`/api/music/${guildId}/${action}`, {
                method: 'POST'
            });
            
            if (response.ok) {
                this.selectMusicServer(guildId); // Refresh data
            }
        } catch (error) {
            console.error('Error music action:', error);
        }
    }

    async createCustomCommand() {
        const name = document.getElementById('cmd-name').value;
        const description = document.getElementById('cmd-description').value;
        const response = document.getElementById('cmd-response').value;

        if (!name || !response) {
            alert('Nama command dan response harus diisi');
            return;
        }

        try {
            const res = await fetch('/api/commands/custom', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    name: name,
                    description: description,
                    response: response
                })
            });

            if (res.ok) {
                alert('Custom command berhasil dibuat');
                this.loadCustomCommandsData();
                // Clear form
                document.getElementById('cmd-name').value = '';
                document.getElementById('cmd-description').value = '';
                document.getElementById('cmd-response').value = '';
            }
        } catch (error) {
            console.error('Error creating custom command:', error);
        }
    }

    async logout() {
        try {
            await fetch('/auth/logout');
            window.location.href = '/login';
        } catch (error) {
            console.error('Logout error:', error);
        }
    }

    updateVolume(volume) {
        console.log('Volume updated to:', volume);
    }
}

// Initialize dashboard when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.dashboard = new Dashboard();
});

// Global functions for onclick events
function musicAction(action) {
    window.dashboard.musicAction(action);
}

function createCustomCommand() {
    window.dashboard.createCustomCommand();
}

function logout() {
    window.dashboard.logout();
}

function selectGuild(guildId) {
    console.log('Selected guild:', guildId);
}
