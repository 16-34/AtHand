import { invoke } from '@tauri-apps/api/tauri';
import { listen } from '@tauri-apps/api/event';
import { appWindow, LogicalSize } from '@tauri-apps/api/window';

// DOM Elements
const searchInput = document.getElementById('search-input');
const settingsBtn = document.getElementById('settings-btn');
const answerPanel = document.getElementById('answer-panel');
const answerContent = document.getElementById('answer-content');
const searchBar = document.getElementById('search-bar');
const statusText = document.getElementById('status-text');
const hintText = document.getElementById('hint-text');

const compactSize = new LogicalSize(656, 68);
const answerSize = new LogicalSize(656, 500);
const settingsSize = new LogicalSize(656, 620);

// Settings Dialog Elements
const settingsOverlay = document.getElementById('settings-overlay');
const apiBaseInput = document.getElementById('api-base');
const apiKeyInput = document.getElementById('api-key');
const modelInput = document.getElementById('model');
const temperatureInput = document.getElementById('temperature');
const tempValue = document.getElementById('temp-value');
const maxTokensInput = document.getElementById('max-tokens');
const toggleKeyBtn = document.getElementById('toggle-key');
const testBtn = document.getElementById('test-btn');
const testResult = document.getElementById('test-result');
const saveBtn = document.getElementById('save-btn');
const cancelBtn = document.getElementById('cancel-btn');

// State
let isProcessing = false;
let config = {};

// Initialize
async function init() {
  await loadConfig();
  setupEventListeners();
  setupKeyboardShortcuts();

  if (!config.api_key) {
    await showSettings();
  }

  searchInput.focus();
}

async function loadConfig() {
  try {
    config = await invoke('get_config');
    apiBaseInput.value = config.api_base || '';
    apiKeyInput.value = config.api_key || '';
    modelInput.value = config.model || 'gpt-4o-mini';
    temperatureInput.value = Math.round((config.temperature || 0.7) * 10);
    tempValue.textContent = (config.temperature || 0.7).toFixed(1);
    maxTokensInput.value = config.max_tokens || 4096;
  } catch (e) {
    console.error('Failed to load config:', e);
  }
}

function setupEventListeners() {
  // Search input
  searchInput.addEventListener('keydown', async (e) => {
    if (e.key === 'Enter' && !isProcessing) {
      const query = searchInput.value.trim();
      if (query) {
        await sendMessage(query);
      }
    }
  });

  // Settings button
  settingsBtn.addEventListener('click', () => {
    void showSettings();
  });

  // Temperature slider
  temperatureInput.addEventListener('input', (e) => {
    tempValue.textContent = (e.target.value / 10).toFixed(1);
  });

  // Toggle API key visibility
  toggleKeyBtn.addEventListener('click', () => {
    if (apiKeyInput.type === 'password') {
      apiKeyInput.type = 'text';
      toggleKeyBtn.textContent = 'Hide';
    } else {
      apiKeyInput.type = 'password';
      toggleKeyBtn.textContent = 'Show';
    }
  });

  // Test connection
  testBtn.addEventListener('click', async () => {
    testBtn.disabled = true;
    testBtn.textContent = 'Testing...';
    testResult.textContent = '';
    testResult.className = 'test-result';

    try {
      const result = await invoke('test_connection', {
        apiBase: apiBaseInput.value || 'https://api.openai.com/v1',
        apiKey: apiKeyInput.value,
        model: modelInput.value || 'gpt-4o-mini'
      });
      testResult.textContent = result;
      testResult.className = 'test-result status-success';
    } catch (e) {
      testResult.textContent = e.toString();
      testResult.className = 'test-result status-error';
    }

    testBtn.disabled = false;
    testBtn.textContent = 'Test Connection';
  });

  // Save settings
  saveBtn.addEventListener('click', async () => {
    const newConfig = {
      api_base: apiBaseInput.value || 'https://api.openai.com/v1',
      api_key: apiKeyInput.value,
      model: modelInput.value || 'gpt-4o-mini',
      temperature: parseFloat(tempValue.textContent),
      max_tokens: parseInt(maxTokensInput.value),
      hotkey: config.hotkey || 'double_shift',
      theme: config.theme || 'dark'
    };

    try {
      await invoke('save_config', { newConfig });
      config = newConfig;
      await hideSettings();
    } catch (e) {
      alert('保存失败: ' + e);
    }
  });

  // Cancel settings
  cancelBtn.addEventListener('click', () => {
    void hideSettings();
  });

  // Listen for show-settings event from Rust
  listen('show-settings', async () => {
    await showSettings();
  });
}

function setupKeyboardShortcuts() {
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
      if (settingsOverlay.classList.contains('visible')) {
        void hideSettings();
      } else {
        void hideWindow();
      }
    }
  });
}

async function sendMessage(query) {
  if (isProcessing) return;
  
  isProcessing = true;
  searchInput.disabled = true;
  
  // Show answer panel
  answerPanel.classList.add('visible');
  searchBar.classList.add('has-answer');
  
  // Add user message to history display
  const userMsgDiv = document.createElement('div');
  userMsgDiv.className = 'user-message';
  userMsgDiv.textContent = query;
  answerContent.appendChild(userMsgDiv);
  
  // Create assistant message container
  const assistantDiv = document.createElement('div');
  assistantDiv.className = 'assistant-message';
  answerContent.appendChild(assistantDiv);
  
  statusText.textContent = '思考中...';
  statusText.className = 'status-thinking';
  hintText.style.display = 'none';
  
  // Resize window for answer
  await appWindow.setSize(answerSize);
  
  try {
    statusText.textContent = '回答中...';
    const response = await invoke('send_message', { message: query });
    
    // Render markdown
    assistantDiv.innerHTML = marked.parse(response);
    
    // Render KaTeX
    if (window.renderMathInElement) {
      renderMathInElement(assistantDiv, {
        delimiters: [
          { left: '$$', right: '$$', display: true },
          { left: '$', right: '$', display: false },
          { left: '\\(', right: '\\)', display: false },
          { left: '\\[', right: '\\]', display: true }
        ],
        throwOnError: false
      });
    }
    
    statusText.textContent = '';
    hintText.style.display = 'inline';
    
    // Clear input for next question
    searchInput.value = '';
    
  } catch (e) {
    assistantDiv.innerHTML = `<span style="color: var(--error)">⚠️ ${escapeHtml(e.toString())}</span>`;
    statusText.textContent = '出错了';
    statusText.className = 'status-error';
    hintText.style.display = 'inline';
  }
  
  isProcessing = false;
  searchInput.disabled = false;
  searchInput.focus();
}

async function showSettings() {
  await appWindow.setSize(settingsSize);
  await appWindow.center();
  settingsOverlay.classList.add('visible');
}

async function hideSettings() {
  settingsOverlay.classList.remove('visible');
  await appWindow.setSize(answerPanel.classList.contains('visible') ? answerSize : compactSize);
  await appWindow.center();
  searchInput.focus();
}

async function hideWindow() {
  await appWindow.hide();

  // Clear conversation
  answerContent.innerHTML = '';
  answerPanel.classList.remove('visible');
  searchBar.classList.remove('has-answer');
  searchInput.value = '';
  statusText.textContent = '';
  
  // Reset window size
  settingsOverlay.classList.remove('visible');
  await appWindow.setSize(compactSize);
}

function escapeHtml(text) {
  const div = document.createElement('div');
  div.textContent = text;
  return div.innerHTML;
}

// Start
init();
