const { contextBridge, ipcRenderer, webUtils } = require('electron')

contextBridge.exposeInMainWorld('pichkooDesktop', {
  getConnection: profile => ipcRenderer.invoke('pichkoo:connection', profile),
  revalidateConnection: () => ipcRenderer.invoke('pichkoo:connection:revalidate'),
  touchBackend: profile => ipcRenderer.invoke('pichkoo:backend:touch', profile),
  getGatewayWsUrl: profile => ipcRenderer.invoke('pichkoo:gateway:ws-url', profile),
  openSessionWindow: sessionId => ipcRenderer.invoke('pichkoo:window:openSession', sessionId),
  getBootProgress: () => ipcRenderer.invoke('pichkoo:boot-progress:get'),
  getConnectionConfig: profile => ipcRenderer.invoke('pichkoo:connection-config:get', profile),
  saveConnectionConfig: payload => ipcRenderer.invoke('pichkoo:connection-config:save', payload),
  applyConnectionConfig: payload => ipcRenderer.invoke('pichkoo:connection-config:apply', payload),
  testConnectionConfig: payload => ipcRenderer.invoke('pichkoo:connection-config:test', payload),
  probeConnectionConfig: remoteUrl => ipcRenderer.invoke('pichkoo:connection-config:probe', remoteUrl),
  oauthLoginConnectionConfig: remoteUrl => ipcRenderer.invoke('pichkoo:connection-config:oauth-login', remoteUrl),
  oauthLogoutConnectionConfig: remoteUrl => ipcRenderer.invoke('pichkoo:connection-config:oauth-logout', remoteUrl),
  profile: {
    get: () => ipcRenderer.invoke('pichkoo:profile:get'),
    set: name => ipcRenderer.invoke('pichkoo:profile:set', name)
  },
  api: request => ipcRenderer.invoke('pichkoo:api', request),
  notify: payload => ipcRenderer.invoke('pichkoo:notify', payload),
  requestMicrophoneAccess: () => ipcRenderer.invoke('pichkoo:requestMicrophoneAccess'),
  readFileDataUrl: filePath => ipcRenderer.invoke('pichkoo:readFileDataUrl', filePath),
  readFileText: filePath => ipcRenderer.invoke('pichkoo:readFileText', filePath),
  selectPaths: options => ipcRenderer.invoke('pichkoo:selectPaths', options),
  writeClipboard: text => ipcRenderer.invoke('pichkoo:writeClipboard', text),
  saveImageFromUrl: url => ipcRenderer.invoke('pichkoo:saveImageFromUrl', url),
  saveImageBuffer: (data, ext) => ipcRenderer.invoke('pichkoo:saveImageBuffer', { data, ext }),
  saveClipboardImage: () => ipcRenderer.invoke('pichkoo:saveClipboardImage'),
  getPathForFile: file => {
    try {
      return webUtils.getPathForFile(file) || ''
    } catch {
      return ''
    }
  },
  normalizePreviewTarget: (target, baseDir) => ipcRenderer.invoke('pichkoo:normalizePreviewTarget', target, baseDir),
  watchPreviewFile: url => ipcRenderer.invoke('pichkoo:watchPreviewFile', url),
  stopPreviewFileWatch: id => ipcRenderer.invoke('pichkoo:stopPreviewFileWatch', id),
  setTitleBarTheme: payload => ipcRenderer.send('pichkoo:titlebar-theme', payload),
  setPreviewShortcutActive: active => ipcRenderer.send('pichkoo:previewShortcutActive', Boolean(active)),
  openExternal: url => ipcRenderer.invoke('pichkoo:openExternal', url),
  fetchLinkTitle: url => ipcRenderer.invoke('pichkoo:fetchLinkTitle', url),
  sanitizeWorkspaceCwd: cwd => ipcRenderer.invoke('pichkoo:workspace:sanitize', cwd),
  settings: {
    getDefaultProjectDir: () => ipcRenderer.invoke('pichkoo:setting:defaultProjectDir:get'),
    setDefaultProjectDir: dir => ipcRenderer.invoke('pichkoo:setting:defaultProjectDir:set', dir),
    pickDefaultProjectDir: () => ipcRenderer.invoke('pichkoo:setting:defaultProjectDir:pick')
  },
  revealLogs: () => ipcRenderer.invoke('pichkoo:logs:reveal'),
  getRecentLogs: () => ipcRenderer.invoke('pichkoo:logs:recent'),
  readDir: dirPath => ipcRenderer.invoke('pichkoo:fs:readDir', dirPath),
  gitRoot: startPath => ipcRenderer.invoke('pichkoo:fs:gitRoot', startPath),
  terminal: {
    dispose: id => ipcRenderer.invoke('pichkoo:terminal:dispose', id),
    resize: (id, size) => ipcRenderer.invoke('pichkoo:terminal:resize', id, size),
    start: options => ipcRenderer.invoke('pichkoo:terminal:start', options),
    write: (id, data) => ipcRenderer.invoke('pichkoo:terminal:write', id, data),
    onData: (id, callback) => {
      const channel = `pichkoo:terminal:${id}:data`
      const listener = (_event, payload) => callback(payload)
      ipcRenderer.on(channel, listener)
      return () => ipcRenderer.removeListener(channel, listener)
    },
    onExit: (id, callback) => {
      const channel = `pichkoo:terminal:${id}:exit`
      const listener = (_event, payload) => callback(payload)
      ipcRenderer.on(channel, listener)
      return () => ipcRenderer.removeListener(channel, listener)
    }
  },
  onClosePreviewRequested: callback => {
    const listener = () => callback()
    ipcRenderer.on('pichkoo:close-preview-requested', listener)
    return () => ipcRenderer.removeListener('pichkoo:close-preview-requested', listener)
  },
  onOpenUpdatesRequested: callback => {
    const listener = () => callback()
    ipcRenderer.on('pichkoo:open-updates', listener)
    return () => ipcRenderer.removeListener('pichkoo:open-updates', listener)
  },
  onWindowStateChanged: callback => {
    const listener = (_event, payload) => callback(payload)
    ipcRenderer.on('pichkoo:window-state-changed', listener)
    return () => ipcRenderer.removeListener('pichkoo:window-state-changed', listener)
  },
  onPreviewFileChanged: callback => {
    const listener = (_event, payload) => callback(payload)
    ipcRenderer.on('pichkoo:preview-file-changed', listener)
    return () => ipcRenderer.removeListener('pichkoo:preview-file-changed', listener)
  },
  onBackendExit: callback => {
    const listener = (_event, payload) => callback(payload)
    ipcRenderer.on('pichkoo:backend-exit', listener)
    return () => ipcRenderer.removeListener('pichkoo:backend-exit', listener)
  },
  onPowerResume: callback => {
    const listener = () => callback()
    ipcRenderer.on('pichkoo:power-resume', listener)
    return () => ipcRenderer.removeListener('pichkoo:power-resume', listener)
  },
  onBootProgress: callback => {
    const listener = (_event, payload) => callback(payload)
    ipcRenderer.on('pichkoo:boot-progress', listener)
    return () => ipcRenderer.removeListener('pichkoo:boot-progress', listener)
  },
  // First-launch bootstrap progress -- emitted by the install.ps1 stage
  // runner in main.cjs (apps/desktop/electron/bootstrap-runner.cjs).
  // Renderer's install overlay subscribes to live events and queries the
  // current snapshot via getBootstrapState() to recover after a devtools
  // reload mid-bootstrap.
  getBootstrapState: () => ipcRenderer.invoke('pichkoo:bootstrap:get'),
  resetBootstrap: () => ipcRenderer.invoke('pichkoo:bootstrap:reset'),
  repairBootstrap: () => ipcRenderer.invoke('pichkoo:bootstrap:repair'),
  cancelBootstrap: () => ipcRenderer.invoke('pichkoo:bootstrap:cancel'),
  onBootstrapEvent: callback => {
    const listener = (_event, payload) => callback(payload)
    ipcRenderer.on('pichkoo:bootstrap:event', listener)
    return () => ipcRenderer.removeListener('pichkoo:bootstrap:event', listener)
  },
  getVersion: () => ipcRenderer.invoke('pichkoo:version'),
  uninstall: {
    summary: () => ipcRenderer.invoke('pichkoo:uninstall:summary'),
    run: mode => ipcRenderer.invoke('pichkoo:uninstall:run', { mode })
  },
  updates: {
    check: () => ipcRenderer.invoke('pichkoo:updates:check'),
    apply: opts => ipcRenderer.invoke('pichkoo:updates:apply', opts),
    getBranch: () => ipcRenderer.invoke('pichkoo:updates:branch:get'),
    setBranch: name => ipcRenderer.invoke('pichkoo:updates:branch:set', name),
    onProgress: callback => {
      const listener = (_event, payload) => callback(payload)
      ipcRenderer.on('pichkoo:updates:progress', listener)
      return () => ipcRenderer.removeListener('pichkoo:updates:progress', listener)
    }
  },
  themes: {
    fetchMarketplace: id => ipcRenderer.invoke('pichkoo:vscode-theme:fetch', id),
    searchMarketplace: query => ipcRenderer.invoke('pichkoo:vscode-theme:search', query)
  }
})
