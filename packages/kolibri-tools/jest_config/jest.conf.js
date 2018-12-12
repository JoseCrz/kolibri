const path = require('path');
const apiSpecAliases = require('../lib/apiSpecExportTools').coreAliases();
const babelConfig = require('../.babelrc.js');

const moduleNameMapper = {
  '^testUtils$': path.resolve(__dirname, './testUtils'),
};

Object.keys(apiSpecAliases).forEach(key => {
  moduleNameMapper['^' + key.replace(/\./g, '\\.') + '$'] = apiSpecAliases[key];
});

module.exports = {
  globals: {
    __kolibriModuleName: 'testmodule',
    __version: 'testversion',
    __copyrightYear: '2018',
    'vue-jest': {
      babelConfig,
    },
  },
  rootDir: path.resolve(process.cwd()),
  moduleFileExtensions: ['js', 'json', 'vue'],
  moduleNameMapper,
  testURL: 'http://kolibri.time',
  transform: {
    '^.+\\.js$': path.resolve(__dirname, './babel-jest-transform'),
    '.*\\.(vue)$': 'vue-jest',
  },
  snapshotSerializers: ['jest-serializer-vue'],
  setupFiles: [path.resolve(__dirname, './setup')],
  coverageDirectory: '<rootDir>/coverage',
  verbose: false,
};
