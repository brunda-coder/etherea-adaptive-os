const NodePolyfillPlugin = require('node-polyfill-webpack-plugin');

module.exports = function override(config, env) {
  // Add the NodePolyfillPlugin to the plugins array
  config.plugins.push(new NodePolyfillPlugin());

  // Add a fallback for the 'fs' module
  config.resolve.fallback = {
    ...config.resolve.fallback,
    fs: false, // You can also use a specific polyfill here if needed
  };

  return config;
};
