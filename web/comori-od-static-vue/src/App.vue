<template>
    <v-app>
        <v-main>
            <v-container mt-0 pt-0>
                <v-row align="center" justify="center">
                    <v-col cols="12" sm="12" md="12" lg="10" xl="8">
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
                              <v-toolbar-title class="ml-3">Comorile Oastei Domnului</v-toolbar-title>
                              <v-spacer></v-spacer>
                                <v-autocomplete
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
                                  item-text="title"
                                  item-value="id"
                                  label="Caută în Comorile Oastei Domnului"
                                  class="mt-7"
                                  append-icon="mdi-magnify">
                                  <template v-slot:item="{item}">
                                    <v-list-item-avatar v-if="item.author === 'Traian Dorz'">
                                      <img :src="require('../src/assets/td.png')">
                                    </v-list-item-avatar>
                                    <v-list-item-content>
                                      <v-list-item-title v-text="item.title"></v-list-item-title>
                                      <v-list-item-subtitle v-text="item.subtitle"></v-list-item-subtitle>
                                    </v-list-item-content>
                                  </template>
                                </v-autocomplete>
                            </v-app-bar>
                            <v-sheet id="content" ref="content" class="overflow-y-auto" :max-height="documentHeight">
                            <v-card-text class="mt-10 height: 100%">
                              <router-view/>
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
        index: "od2",
    }),
    mounted() {
      console.log(shared)
    },
    methods: {
      filter(item, queryText, itemText) {
        item;
        queryText;
        itemText;
        return true;
      },
      goHome() {
        this.$router.push({path: '/'});
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
      }
    },
    computed: {
      documentHeight: function() {
        return window.innerHeight - 40;
      }
    },
    watch: {
        "autocomplete.selected"(val) {
          console.log("Selected: " + val);
          this.$router.push({name: 'Article', params: {id: val}});
          this.autocomplete.prefix = "";
          this.autocomplete.items = [];
        },
        "autocomplete.prefix"(val) {
            if (!val || val.length < 1) {
                this.autocomplete.items = [];
                return;
            }

            this.autocomplete.loading = true;

            let url = shared.base_url + this.index + '/titles/completion?prefix=' + encodeURIComponent(val);
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
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  color: #2c3e50;
}

.notranslate {
  transform: none!important;
}

</style>