<template>
    <div v-if="article">
        <v-list-item class="px-3 px-lg-5">
          <v-list-item-content>
            <v-layout row>
              <v-col class="d-none d-sm-flex" cols=3 md=2>
                <v-list-item-avatar width="75" height="80" v-if="article._source.author === 'Traian Dorz'">
                    <v-img :src="require('../../src/assets/td.png?vuetify-loader')">
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
              </v-col>
              <v-col>
                <v-list-item-title class="text-h5 text-md-h4 text-lg-h3 wrap-text">
                    {{article._source.title}}
                </v-list-item-title>
                <v-list-item-subtitle class="text-subtitle-1 wrap-text">
                    {{article._source.book}} - {{article._source.author}}
                </v-list-item-subtitle>
              </v-col>
            </v-layout>
            <div id="content" class="mt-5">
                <template v-for="(contents, verseIndex) in article._source.verses">
                    <component v-bind:is="getTagName(verseIndex)" v-if="contents.length !== 0" :key="verseIndex" class="text-body-1 mb-0">
                        <template v-for="(content, blockIndex) in contents"><span v-if="content.type == 'normal'" class="normal" v-bind:style="getBlockStyle(verseIndex, blockIndex)" :key="verseIndex + ':' + blockIndex">{{content.text}}</span>
                            <v-tooltip 
                                top 
                                href='#' 
                                v-model="show[content.text + verseIndex]" 
                                color="grey darken-3"
                                class="bible-ref" 
                                v-else-if="content.type == 'bible-ref'" :key="verseIndex + ':' + blockIndex">
                                <template v-slot:activator="{on, attrs}">
                                    <a href='#' @click.prevent="show[content.text + verseIndex] = true" v-bind="attrs" v-on="on">{{content.text}}</a>
                                </template>
                                <template v-if="article._source['bible-refs'][content.ref]">
                                    <p v-for="verse in article._source['bible-refs'][content.ref].verses" 
                                       :key="verse.name"
                                       class="mb-0">
                                       <b>{{verse.name}}:</b> {{verse.text}}
                                    </p>
                                </template>
                                <template v-else>
                                    <p class="mb-0">
                                        Verset inexistent!
                                    </p>
                                </template>
                            </v-tooltip>
                        </template>
                    </component>
                    <br v-if="!isParagraph(verseIndex)" :key="verseIndex + '_break'"/>
                </template>
                <div id="similars" class="mt-5" v-if="similars.length > 0">
                    <h2 class="text-subtitle-1 text-sm-h5">Vezi pe aceeași temă:</h2>
                    <v-card v-for="similar in similars" :key="similar._id">
                        <v-list-item>
                          <v-list-item-avatar size=50 v-if="similar._source.author === 'Traian Dorz'">
                            <img :src="require('../../src/assets/td.png')">
                          </v-list-item-avatar>
                          <v-list-item-content>
                            <router-link :to="{ name: 'Article', params: {id: similar._id}}">
                                <v-list-item-title class="text-subtitle-1 text-sm-h5">
                                     {{similar._source.title}}
                                </v-list-item-title>
                            </router-link>
                            <v-list-item-subtitle class="text-subtitle-1 text-sm-h5">{{similar._source.book}} - {{similar._source.author}}</v-list-item-subtitle>
                          </v-list-item-content>
                        </v-list-item>
                    </v-card>
                </div>
            </div>
          </v-list-item-content>
        </v-list-item>
    </div>
    <v-layout v-else
          fill-height
          align-center
          justify-center
          mt-5
          mx-0
        >
      <v-progress-circular indeterminate color="grey lighten-3"></v-progress-circular>
    </v-layout>
</template>

<script>
import shared from '../components/Shared'

export default {
    name: "Article",
    data() {
        return {
            id: null,
            article: null,
            show: {},
            contentElement: null,
            similars: []
        }
    },
    mounted() {
        this.getById(this.$route.params.id);
        //this.getSimilar(this.$route.params.id);
    },
    watch: {
        article(to, from) {
            from;
            document.title = "Comori OD: " + to._source.title + ", " + to._source.book + " - " + to._source.author;
        },
        $route(to, from) {
            from;
            let id = to.params.id;
            if (id !== this.id)
            {
                this.getById(id);
            }
        }
    },
    methods: {
        getFontWeight(verseIndex, blockIndex) {
            if (this.article._source.verses[verseIndex][blockIndex]['style'].includes('bold'))
                return "bold"
            else
                return "normal"
        },
        getFontStyle(verseIndex, blockIndex) {
            if (this.article._source.verses[verseIndex][blockIndex]['style'].includes('italic'))
                return "italic"
            else
                return "normal"
        },
        getBlockStyle(verseIndex, blockIndex) {
            return { 
                'font-weight': this.getFontWeight(verseIndex, blockIndex), 
                'font-style': this.getFontStyle(verseIndex, blockIndex) 
            }
        },
        isParagraph(index) {
            if (index === 0)
            {
                return true;
            }

            if (this.article._source.verses[index - 1].length === 0)
            {
                return true;
            }

            return false;
        },
        getTagName(index) {
            if (this.isParagraph(index))
                return "p";
            else
                return "span";
        },
        getSimilar(id) {
            let url = shared.base_url + shared.index_name + '/articles/similar?id=' + encodeURIComponent(id)
            console.log("Getting similars from " + url)
            fetch(url)
                .then(response => response.json())
                .then(response => {
                    if (response.exception)
                    {
                        console.log("Error: " + response.exception)
                        return;
                    }

                    this.similars = response.hits.hits;
                })
        },
        getById(id) {
            let url = shared.base_url + shared.index_name + '/articles?id=' + encodeURIComponent(id)
            console.log("Getting by id from " + url);
            fetch(url)
                .then(response => response.json())
                .then(response => {
                    if (response.exception)
                    {
                        console.log("Error: " + response.exception);
                        return;
                    }

                    this.article = response;
                });
            this.id = id;
        }
    }
}
</script>
<style lang="scss">
 @import '@/scss/shared-styles.scss';
</style>