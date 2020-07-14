<template>
    <div class="search">
        <v-list-item>
          <v-list-item-content class="mt-3">
            <template v-if="loading">
                <v-layout
                      fill-height
                      align-center
                      justify-center
                      ma-0
                    >
                  <v-progress-circular indeterminate color="grey lighten-3"></v-progress-circular>
                </v-layout>
            </template>
            <template v-else-if="!loading && total === 0">
                <v-list-item-title class="text-subtitle-1 text-sm-h5 wrap-text">Nu am găsit rezultate despre '{{q}}'.</v-list-item-title>
                <v-list-item-subtitle class="text-subtitle-1 text-sm-h5 wrap-text" v-if="suggest">
                    Vrei să cauți
                    <router-link :to="{ name: 'Search', params: {q: suggest}}">
                        {{suggest}}
                    </router-link>
                    ?
                </v-list-item-subtitle>
            </template>
            <template v-else-if="!loading && total === 1">
                <v-list-item-title class="text-subtitle-1 text-sm-h5 wrap-text">Am găsit un singur rezultat despre '{{q}}' în {{took}} milisecunde.".</v-list-item-title>
                <v-list-item-subtitle></v-list-item-subtitle>
            </template>
            <template v-else>
                <v-list-item-title class="text-subtitle-1 text-sm-h5 wrap-text">Am găsit {{total}} rezultate despre '{{q}}' în {{took}} milisecunde."</v-list-item-title>
            </template>            
          </v-list-item-content>
        </v-list-item>
        <transition-group name="slide-fade">
        <v-card v-for="(hit, index) in hits" :key="hit._id"
            class="ma-2 ma-sm-3 ma-md-5"
            outlined
          >
          <v-list-item class="py-1 py-sm-3 py-md-5 px-3 px-md-5">
              <v-list-item-avatar width="48" height="50" v-if="hit._source.author === 'Traian Dorz'">
                <v-img :src="require('../../src/assets/td-50.jpg?vuetify-preload')">
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
                <router-link :to="{ name: 'Article', params: {id: hit._id}}">
                    <v-list-item-title 
                        v-if="hit.highlight && hit.highlight.title"
                        class="text-subtitle-1 text-sm-h5 wrap-text"
                        v-html="index + 1 + '. ' + hit.highlight.title[0]">
                    </v-list-item-title>
                    <v-list-item-title v-else class="text-subtitle-1 text-sm-h5 wrap-text">
                        {{index + 1}}. {{hit._source.title}}
                    </v-list-item-title>
                </router-link>
                <v-list-item-subtitle class="wrap-text">{{hit._source.book}} - {{hit._source.author}}</v-list-item-subtitle>
              </v-list-item-content>
            </v-list-item>
            <v-card-text class="pt-0 pb-1 pb-sm-3 pb-md5 px-3 px-md-5">
                <template v-if="hit.highlight && hit.highlight['verses.text']">
                  <p v-for="(line, index) in hit.highlight['verses.text']" :key="index" v-html="line" class="mb-2"/>
                </template>
            </v-card-text>
        </v-card>
    </transition-group>
        <v-layout v-if="offset > 0 && loading"
              fill-height
              align-center
              justify-center
              ma-0
            >
          <v-progress-circular indeterminate color="grey lighten-3"></v-progress-circular>
        </v-layout>
    </div>
</template>
<script>
import shared from '../components/Shared'

export default {
    name: "Search",
    data() {
        return {
            q: null,
            loading: false,
            suggest: null,
            total: 0,
            took: null,
            hits: [],
            offset: 0,
            limit: 10,
            index: "od2",
            contentElement: null
        }
    },
    watch: {
        q(to, from) {
            from;
            document.title = "Comori OD: Caută '" + to + "'";
        },
        $route(to, from) {
            from;
            let q = to.params.q;
            if (q !== this.q)
            {
                this.offset = 0;
                this.query(q, this.offset, this.limit);
            }
        }
    },
    mounted() {
        // need to use plain Javascript querySelector, as the element is outside this component
        // and can't be accessed by ref
        this.contentElement = document.querySelector('#content');
        this.contentElement.addEventListener('scroll', this.handleScroll);

        this.query(this.$route.params.q, this.offset, this.limit);
    },
    methods: {
        query(q, offset, limit) {
            this.loading = true;

            let url = shared.base_url + this.index + '/articles?q=' + encodeURIComponent(q) + '&offset=' + offset + '&limit=' + limit;

            console.log('Searching ' + url);
            fetch(url)
              .then(response => response.json())
              .then(response => {
                if (response.exception)
                {
                    console.log("Error: " + response.exception);
                    return;
                }

                if (q !== this.q || offset === 0)
                {
                    this.total = response.hits.total.value;
                    this.took = response.took;
                    this.hits = response.hits.hits;

                    if (this.hits < 2)
                    {
                        this.suggestQuery(q);
                    }
                }
                else
                {
                    this.hits = this.hits.concat(response.hits.hits);
                }

                this.q = q;
                this.offset = offset;
                this.limit = limit;

                this.loading = false;
              });          
        },
        suggestQuery(q) {
            let url = shared.base_url + this.index + '/suggest?q=' + encodeURIComponent(q);
            console.log('Suggesting ' + url); 
            fetch(url)
                .then(response => response.json())
                .then(response => {
                    if (response.exception)
                    {
                        console.log("Error: " + response.exception);
                        return;
                    }

                    if (response.suggest.simple_phrase[0].options.length > 0)
                    {
                        this.suggest = response.suggest.simple_phrase[0].options[0].text;
                    }
                });
        },
        handleScroll() {
            let scrollAtBottom = this.contentElement.scrollTop + this.contentElement.offsetHeight === this.contentElement.scrollHeight;

            if(this.offset < this.total && this.q && scrollAtBottom ) {
                this.offset += this.limit;
                this.query(this.q, this.offset, this.limit);
            }
        }
    }
}
</script>
<style lang="scss">
 @import '@/scss/shared-styles.scss';
</style>