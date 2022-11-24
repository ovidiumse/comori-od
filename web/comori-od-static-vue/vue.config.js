module.exports = {
  "transpileDependencies": [
    "vuetify"
  ],
  chainWebpack: config => {
    config.plugin('VuetifyLoaderPlugin').tap(() => [{
      progressiveImages: {
        size: 12,
        sharp: true
      }
    }])
    config.resolve.symlinks(false)
  }
}