import Vue from 'vue';
import Vuetify from 'vuetify/lib/framework';
import colors from 'vuetify/lib/util/colors'

Vue.use(Vuetify);

export default new Vuetify({
  theme: {
    themes: {
      light: {
        primary: '#F05033',
        secondary: '#40C463',
        warning: colors.orange.base,
        error: colors.pink.base,
        success: '#40C463',
      }
    }
  }
});
