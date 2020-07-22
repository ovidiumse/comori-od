<template>
    <v-app>
        <v-main>
            <v-container mt-0 pt-0>
                <v-row align="center" justify="center">
                    <v-col cols="12" sm="12" md="12" lg="10" xl="8" class="pa-0 pa-sm-1">
                        <v-card color="grey lighten-5" >
                            <v-app-bar 
                              ref="appbar"
                              color="grey darken-3" 
                              absolute
                              dense 
                              dark 
                              elevation="1"
                              scroll-target="#content">
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
                                      <v-img :src="require('../src/assets/td-50.jpg?vuetify-preload')">
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
                            <v-sheet id="content" ref="content" class="overflow-y-auto" :max-height="documentHeight">
                            <v-card-text class="mt-5 mt-sm-10 px-0 px-sm-1 height: 100%">
                              <keep-alive include="Search">
                                <router-view></router-view>
                              </keep-alive>
                            </v-card-text>
                          </v-sheet>
                        </v-card>
                    </v-col>
                </v-row>
            </v-container>
        </v-main>
    </v-app>
</template>
<script>

import shared from './components/Shared'

export default {
    name: 'App',
    components: {},

    data: () => ({
        autocomplete: {
            loading: false,
            errored: false,
            prefix: "",
            selected: null,
            items: []
        },
        title: "Comorile Oastei Domnului",
        index: "od2",
        showSearch: false
    }),
    created() {
      if (this.isMobile)
      {
        this.title = "Comori OD";
      }

      document.title = this.title;
    },
    mounted() {
      this.showSearch = !this.isMobile;
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
        return window.innerHeight - 20;
      },
      isMobile: function() {
        return this.$vuetify.breakpoint.mobile;
      }
    },
    watch: {
        "autocomplete.selected"(article) {
          console.log("Selected: " + JSON.stringify(article));
          this.$router.push({name: 'Article', params: {id: article.id}});
          this.autocomplete.prefix = "";
          this.autocomplete.items = [];
        },
        "autocomplete.prefix"(val) {
            if (!val || val.length < 1) {
                this.autocomplete.items = [];
                return;
            }

            this.autocomplete.loading = true;

            let url = shared.base_url + shared.index_name + '/titles/completion?prefix=' + encodeURIComponent(val);
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
        }
    }
};
</script>

<style lang="scss">
@import '@/scss/shared-styles.scss';

#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  color: #2c3e50;
}

</style>