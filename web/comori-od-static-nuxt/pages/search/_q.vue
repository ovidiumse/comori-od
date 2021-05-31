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
                    <router-link :to="{ name: 'search-q', params: {q: suggest}}">
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
                <v-img src="/td-50.jpg?vuetify-preload">
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
                <v-list-item-title 
                    v-if="hit.highlight && hit.highlight.title"
                    class="text-subtitle-1 text-sm-h5 wrap-text">
                    <router-link 
                        :to="{ name: 'article-id', params: {id: hit._id}}" 
                        v-html="index + 1 + '. ' + hit.highlight.title[0]">
                    </router-link>
                </v-list-item-title>
                <v-list-item-title v-else class="text-subtitle-1 text-sm-h5 wrap-text">
                    <router-link 
                        :to="{ name: 'article-id', params: {id: hit._id}}">
                        {{index + 1}}. {{hit._source.title}}
                    </router-link>
                </v-list-item-title>
                <v-list-item-subtitle class="wrap-text">{{hit._source.book}} - {{hit._source.author}}</v-list-item-subtitle>
              </v-list-item-content>
            </v-list-item>
            <v-card-text class="pt-0 pb-1 pb-sm-3 pb-md5 px-3 px-md-5">
                <template v-if="hit.highlight && hit.highlight['verses.text']">
                  <p v-for="(line, index) in hit.highlight['verses.text']" :key="index" v-html="line" class="mb-2"/>
                </template>
            </v-card-text>
        </v-card>
        <v-card key="-1" v-intersect="loadMore">
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
import shared from '~/components/Shared.vue';
import EventBus from '~/components/EventBus.vue';

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
            limit: 20,
            authors: [],
            types: [],
            volumes: [],
            books: [],
        }
    },
    watch: {
        q(to, from) {
            from;
            document.title = "Comori OD: Caută '" + to + "'";
        }
    },
    created() {
        EventBus.$on('requery', (field) => {
            this.query(this.q, this.offset, this.limit, field);
        });
    },
    beforeDestroy() {
        EventBus.$off('requery');
    },
    mounted() {
        this.updateAuthors();
        this.updateTypes();
        this.updateVolumes();
        this.updateBooks();
    },
    async fetch() {
        let q = this.$route.params.q;
        let offset = this.$route.params.offset || 0;
        let limit = this.$route.params.limit || this.limit;
        await this.query(q, offset, limit, true);
    },
    methods: {
        updateAuthors(fieldFilter) {
            console.log('Updating authors counts from ' + fieldFilter + '...');
            shared.authors.splice(this.authors.length);
            for (const [index, bucket] of this.authors.entries()) {
                this.$set(shared.authors, index, bucket);
            }
        },
        updateTypes(fieldFilter) {
            console.log('Updating types counts from ' + fieldFilter + '...');
            shared.types.splice(this.types.length);
            for (const [index, bucket] of this.types.entries()) {
                this.$set(shared.types, index, bucket);
            }
        },
        updateVolumes(fieldFilter) {
            console.log('Updating volumes counts from ' + fieldFilter + '...');
            shared.volumes.splice(this.volumes.length);
            for (const [index, bucket] of this.volumes.entries()) {
                this.$set(shared.volumes, index, bucket);
            }
        },
        updateBooks(fieldFilter) {
            console.log('Updating books counts from ' + fieldFilter + '...');
            shared.books.splice(this.books.length);
            for (const [index, bucket] of this.books.entries()) {
                this.$set(shared.books, index, bucket);
            }
        },
        async aggregate(q, offset, limit, updatedFilter) {
            let authorFilters = [];
            for (const bucket of shared.authors) {
                if ('checked' in bucket && bucket.checked) {
                    authorFilters.push(bucket.author);
                }
            }

            let typeFilters = [];
            for (const bucket of shared.types) {
                if ('checked' in bucket && bucket.checked) {
                    typeFilters.push(bucket.type);
                }
            }

            let volumeFilters = [];
            for (const bucket of shared.volumes) {
                if ('checked' in bucket && bucket.checked) {
                    volumeFilters.push(bucket.volume);
                }
            }

            let bookFilters = [];
            for (const bucket of shared.books) {
                if ('checked' in bucket && bucket.checked) {
                    bookFilters.push(bucket.book);
                }
            }

            let url = shared.getApiUrl() + shared.indexName + '/articles?q=' + encodeURIComponent(q) 
                + '&offset=' + offset + '&limit=' + limit;
            
            if (authorFilters.length && updatedFilter != 'author')
                url += '&authors=' + encodeURIComponent(authorFilters.join(','));

            if (typeFilters.length && updatedFilter != 'type')
                url += '&types=' + encodeURIComponent(typeFilters.join(','));

            if (volumeFilters.length && updatedFilter != 'volume')
                url += '&volumes=' + encodeURIComponent(volumeFilters.join(','));
            
            if (bookFilters.length && updatedFilter != 'book')
                url += '&books=' + encodeURIComponent(bookFilters.join(','));

            console.log('Aggregating for filter ' + updatedFilter + ' with ' + url);

            await fetch(url)
              .then(response => response.json())
              .then(response => {
                if (response.exception)
                {
                    console.log("Error: " + response.exception);
                    return;
                }

                console.log("Response: " + JSON.stringify(response.aggregations, null, 2));

                if (updatedFilter == 'author')
                {
                    this.authors = []
                    for (const bucket of response.aggregations.authors.buckets)
                    {
                        this.authors.push({
                            author: bucket.key,
                            doc_count: bucket.doc_count,
                            checked: authorFilters.includes(bucket.key)
                        });
                    }

                    this.updateAuthors(updatedFilter);
                }

                if (updatedFilter == 'type')
                {
                    this.types = [];
                    for (const bucket of response.aggregations.types.buckets)
                    {
                        this.types.push({
                            type: bucket.key,
                            doc_count: bucket.doc_count,
                            checked: typeFilters.includes(bucket.key)
                        });
                    }

                    this.updateTypes(updatedFilter);
                }

                if (updatedFilter == 'volume')
                {
                    this.volumes = [];
                    for (const bucket of response.aggregations.volumes.buckets)
                    {
                        this.volumes.push({
                            volume: bucket.key,
                            doc_count: bucket.doc_count,
                            checked: volumeFilters.includes(bucket.key)
                        });
                    }

                    this.updateVolumes(updatedFilter);
                }

                if (updatedFilter == 'book')
                {
                    this.books = [];
                    for (const bucket of response.aggregations.books.buckets)
                    {
                        this.books.push({
                            book: bucket.key,
                            doc_count: bucket.doc_count,
                            checked: bookFilters.includes(bucket.key)
                        });
                    }

                    this.updateBooks(updatedFilter);    
                }
              }); 
        },
        async query(q, offset, limit, updatedFilter) {
            this.loading = true;

            let authorFilters = [];
            for (const bucket of shared.authors) {
                if ('checked' in bucket && bucket.checked) {
                    authorFilters.push(bucket.author);
                }
            }

            let typeFilters = [];
            for (const bucket of shared.types) {
                if ('checked' in bucket && bucket.checked) {
                    typeFilters.push(bucket.type);
                }
            }

            let volumeFilters = [];
            for (const bucket of shared.volumes) {
                if ('checked' in bucket && bucket.checked) {
                    volumeFilters.push(bucket.volume);
                }
            }

            let bookFilters = [];
            for (const bucket of shared.books) {
                if ('checked' in bucket && bucket.checked) {
                    bookFilters.push(bucket.book);
                }
            }

            let url = shared.getApiUrl() + shared.indexName + '/articles?q=' + encodeURIComponent(q) 
                + '&offset=' + offset + '&limit=' + limit;
            
            if (authorFilters.length)
                url += '&authors=' + encodeURIComponent(authorFilters.join(','));

            if (typeFilters.length)
                url += '&types=' + encodeURIComponent(typeFilters.join(','));

            if (volumeFilters.length)
                url += '&volumes=' + encodeURIComponent(volumeFilters.join(','));
            
            if (bookFilters.length)
                url += '&books=' + encodeURIComponent(bookFilters.join(','));

            console.log('Searching ' + url);

            if (updatedFilter)
            {
                this.aggregate(q, offset, limit, 'author');
                this.aggregate(q, offset, limit, 'type');
                this.aggregate(q, offset, limit, 'volume');
                this.aggregate(q, offset, limit, 'book');
            }
            else
                this.aggregate(q, offset, limit, '')

            await fetch(url)
              .then(response => response.json())
              .then(response => {
                if (response.exception)
                {
                    console.log("Error: " + response.exception);
                    return;
                }

                if (offset === 0)
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

                if (this.offset === 0)
                {
                    console.log("Scrolling to 0 while searching for " + q + ", offset: " + offset + ", limit: " + limit);
                    //this.contentElement.scrollTop = 0;
                }
              });          
        },
        suggestQuery(q) {
            let url = shared.getApiUrl() + shared.indexName + '/suggest?q=' + encodeURIComponent(q);
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
        loadMore(entries, observer, isIntersecting) {
            if (isIntersecting && !this.loading && this.total > this.offset + this.limit)
            {
                console.log("Load the next " + this.limit + " results...");
                this.offset += this.limit;
                this.query(this.q, this.offset, this.limit);
            }
        }
    }
}
</script>
<style lang="scss">
 @import '@/assets/shared-styles.scss';
</style>