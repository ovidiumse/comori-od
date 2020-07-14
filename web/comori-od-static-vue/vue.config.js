const BundleAnalyzerPlugin = require('webpack-bundle-analyzer')
    .BundleAnalyzerPlugin;

module.exports = {
  "transpileDependencies": [
    "vuetify"
  ],
  configureWebpack: {
        plugins: [new BundleAnalyzerPlugin()]
   },
  chainWebpack: config => {
    config.plugin('VuetifyLoaderPlugin').tap(args => [{
      progressiveImages: {
      	size: 12,
      	sharp: true
      }
    }])
  }
}