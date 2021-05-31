<template>
  <v-app id="comori-od">
    <v-app-bar app>
      <v-app-bar-nav-icon @click="drawer = !drawer"></v-app-bar-nav-icon>
      <v-btn
        icon 
        @click="goBack">
        <v-icon>mdi-arrow-left</v-icon>
      </v-btn>
      <v-btn
        icon 
        @click="goHome">
        <v-icon>mdi-home</v-icon>
      </v-btn>
      <v-toolbar-title v-show="!showSearch || !isMobile" class="ml-3">{{title}}</v-toolbar-title>
      <v-spacer></v-spacer>
      <v-btn v-if="isMobile" v-show="!showSearch" icon @click="enableSearch">
        <v-icon>mdi-magnify</v-icon>
      </v-btn>
      <transition name="expand">
        <v-autocomplete
          ref="search"
          v-show="showSearch"
          v-on:blur="hideSearch"
          color="grey darken-3"
          v-model="autocomplete.selected"
          :loading="autocomplete.loading"
          :error="autocomplete.errored"
          :error-messages="autocomplete.error"
          :items="autocomplete.items"
          :search-input.sync="autocomplete.prefix"
          :filter="filter"
          @keydown.enter.stop="search"
          @click:append="search"
          single-line
          solo-inverted
          clearable
          dense
          flat
          hide-no-data
          label="Caută în Comorile Oastei Domnului"
          class="mt-7"
          append-icon="mdi-magnify">
          <template v-slot:item="{item}">
            <v-list-item-avatar width="48" height="50" v-if="item.author === 'Traian Dorz'">
              <v-img :src="require('../static/td-50.jpg?vuetify-preload')">
                <template v-slot:placeholder>
                      <v-layout
                        fill-height
                        align-center
                        justify-center
                        ma-0
                      >
                    <v-progress-circular indeterminate color="grey lighten-3"></v-progress-circular>
                  </v-layout>
                </template>
              </v-img>
            </v-list-item-avatar>
            <v-list-item-content>
              <v-list-item-title v-text="item.title"></v-list-item-title>
              <v-list-item-subtitle v-text="item.subtitle"></v-list-item-subtitle>
            </v-list-item-content>
          </template>
        </v-autocomplete>
      </transition>
    </v-app-bar>
    <v-navigation-drawer
      v-model="drawer"
      v-bind:width="360"
      app
    >
      <v-sheet
        color="grey lighten-4"
        class="pa-4"
      >
        <v-avatar
          class="mb-4"
          color="grey darken-1"
          size="64"
        ></v-avatar>

        <div>john@vuetifyjs.com</div>
      </v-sheet>

      <v-divider></v-divider>
      <v-tabs v-model="tab" active-class="active" vertical>
        <v-tab v-for="tab in tabs" :key="tab.tab">{{tab.tab}}</v-tab>
      </v-tabs>
      <v-divider></v-divider>

      <filters/>
     
    </v-navigation-drawer>

    <v-main>
      <v-container
        class="py-8 px-6"
        fluid
      >
        <v-layout justify-center>
          <v-card style="width: 1200px">            
            <v-tabs-items v-model="tab">
              <v-tab-item v-for="tab in tabs" :key="tab.tab" justify-center>    
                <nuxt/>
              </v-tab-item>
            </v-tabs-items>
          </v-card>
        </v-layout>
      </v-container>
    </v-main>
  </v-app>
</template>

<script>

import shared from '../components/Shared.vue';
import Filters from '../components/Filters.vue';

export default {
      name: 'App',
    components: {Filters},

    data: () => ({
      autocomplete: {
          loading: false,
          errored: false,
          prefix: "",
          selected: null,
          items: [],
      },
      tab: null,
      tabs: [
        {tab: 'Explorează', link: '/browse'},
        {tab: 'Caută', link: '/search'},
        {tab: 'Biblia', link: '/bible'}
      ],
      title: "Comorile Oastei Domnului",
      showSearch: false,
      drawer: true,
    }),
    created() {
      if (this.isMobile)
      {
        this.title = "Comori OD";
      }

      if (process.client)
        document.title = this.title;
    },
    mounted() {
      this.showSearch = !this.isMobile;
      console.log("Show search: " + this.showSearch);
    },
    methods: {
      filter(item, queryText, itemText) {
        item;
        queryText;
        itemText;
        return true;
      },
      enableSearch() {
        this.showSearch = true;
        this.$nextTick(() => {
          this.$refs.search.focus();
        });
      },
      hideSearch() {
        this.showSearch = !this.isMobile || false;
      },
      goHome() {
        this.$router.push({path: '/'});
        document.title = this.title;
      },
      goBack() {
        this.$router.go(-1);
      },
      tabChange(value) {
        console.log("Tab changed to " + value)
      },
      search() {
        if (!this.autocomplete.prefix)
        {
          this.autocomplete.error = "Introduceți un termen de căutare.";
          this.autocomplete.errored = true;
          return;
        }

        if (this.autocomplete.prefix.length < 3)
        {
          this.autocomplete.items = [];
          this.autocomplete.error = "Termenul de căutare trebuie sa conțină cel puțin 3 caractere.";
          this.autocomplete.errored = true;
          return;
        }

        this.autocomplete.error = "";
        this.autocomplete.errored = false;

        this.$router.push({path: '/search/' + encodeURIComponent(this.autocomplete.prefix)});

        this.autocomplete.prefix = "";
        this.autocomplete.items = [];

        this.$nextTick(() => {
          this.$refs.search.blur();          
        });
      }
    },
    computed: {
      documentHeight: function() {
        if (process.client)
          return window.innerHeight - 20;
        else
          return 0;
      },
      isMobile: function() {
        console.log("isMobile: " + this.$vuetify.breakpoint.mobile);
        return this.$vuetify.breakpoint.mobile && false;
      }
    },
    watch: {
        tab(idx) {
          console.log("Tab changed to " + this.tabs[idx].tab);
          this.$router.push({path: this.tabs[idx].link});
        },
        "autocomplete.selected"(article) {
          console.log("Selected: " + JSON.stringify(article));
          this.$router.push({name: 'article-id', params: {id: article.id}});
          this.autocomplete.prefix = "";
          this.autocomplete.items = [];
        },
        "autocomplete.prefix"(val) {
            if (!val || val.length < 1) {
                this.autocomplete.items = [];
                return;
            }

            this.autocomplete.loading = true;

            let url = shared.getApiUrl() + shared.indexName + '/titles/completion?prefix=' + encodeURIComponent(val);
            console.log("Completion: " + url);

            fetch(url)
                .then(response => response.json())
                .then(response => {
                  if (response.exception) 
                  {
                    this.autocomplete.errored = true;
                    this.autocomplete.error = "Error: " + response.exception;
                    return;
                  }

                  this.autocomplete.items = response.hits.hits.map(hit => ({
                      id: hit._id,
                      title: hit._source.title, 
                      subtitle: hit._source.book + ' - ' + hit._source.author,
                      book: hit._source.book,
                      author: hit._source.author
                  }));
                })
                .catch(error => {
                    console.log("Error: " + error);
                    this.autocomplete.errored = true;
                    this.autocomplete.error = error.toString();
                })
                .finally(() => {
                    this.autocomplete.loading = false;
                })
        },
    }
};
</script>

<style lang="scss">
@import '@/assets/shared-styles.scss';

#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  color: #2c3e50;
}

</style>
