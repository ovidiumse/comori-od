<template>
  <v-container fluid>
    <v-row dense>
      <v-col v-for="author in authors" :key="author.name">
        <v-card>
          <v-card-title>{{author.name}}</v-card-title>
          <v-card-text>
            <v-list dense>
              <v-list-item v-if="author.books > 0">
                <v-list-item-content>
                  <v-list-item-title v-if="author.books > 1">  {{author.books}} de cărți </v-list-item-title>
                  <v-list-item-title v-else>  {{author.books}} carte </v-list-item-title>
                </v-list-item-content>
              </v-list-item>
              <v-list-item v-if="author.articles > 0">
                <v-list-item-content>
                  <v-list-item-title v-if="author.articles > 1">  {{author.articles}} de articole </v-list-item-title>
                  <v-list-item-title v-else>  {{author.articles}} articol </v-list-item-title>
                </v-list-item-content>
              </v-list-item>
              <v-list-item v-if="author.poems > 0">
                <v-list-item-content>
                  <v-list-item-title v-if="author.poems > 1">  {{author.poems}} de poezii </v-list-item-title>
                  <v-list-item-title v-else>  {{author.poems}} poezie </v-list-item-title>
                </v-list-item-content>
              </v-list-item>
            </v-list>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
import shared from '~/components/Shared.vue'
export default {
  data() {
      return {
          authors: [],
          types: [],
          volumes: [],
          books: [],
      }
  },
  components: {
  },
  mounted() {
    shared.authors.splice(0);
    shared.types.splice(0);
    shared.volumes.splice(0);
    shared.books.splice(0);
  },
  async fetch() {
      await this.getAuthors();
  },
  methods: {
    async get(url, process) {
      let fullUrl = shared.getApiUrl() + shared.indexName + url;
      await fetch(fullUrl)
          .then(response => response.json())
          .then(response => {
            if (response.exception)
            {
                console.log("Error: " + response.exception);
                return;
            }

            process(response);
          });
    },
    getAuthors() {
      var self = this;
      this.get("/authors", function(response){
        for (let authorBucket of response.aggregations.authors.buckets) {
          console.log("Author: " + JSON.stringify(authorBucket, null, 2))
          var author = {"name": authorBucket.key};

          for (let typeBucket of authorBucket.types.buckets) {
            if (typeBucket.key == "poezie")
              author["poems"] = typeBucket.doc_count;
            else if (typeBucket.key == "articol")
              author["articles"] = typeBucket.doc_count;
          }

          author["books"] = authorBucket.books.buckets.length;

          self.authors.push(author);
        }
      });
    },
  }
}
</script>
