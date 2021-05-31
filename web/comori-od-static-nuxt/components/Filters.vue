<template>
    <div>
        <v-card v-if="authors.length" class="ma-3">
            <v-card-title class="h6 py-2">Autori</v-card-title>
            <v-card-text>
                <v-simple-table dense>
                    <tbody>
                        <tr v-for="bucket in authors"
                            :key="bucket.author"
                        >
                            <td class="pa-0" style="height: 22px">
                                <v-checkbox
                                    v-model="bucket.checked"
                                    :label="bucket.author"
                                    @change="checkChange('author')"
                                    dense
                                    style="height: 22px;"
                                    class="mt-0 pa-0"
                                />
                            </td>
                            <td class="pa-0 text-right">
                                {{bucket.doc_count}}
                            </td>
                        </tr>
                    </tbody>
                </v-simple-table>
            </v-card-text>
        </v-card>
        <v-card v-if="types.length" class="ma-3">
            <v-card-title class="h6 py-2">Tip</v-card-title>
            <v-card-text>
                <v-simple-table dense>
                    <tbody>
                        <tr v-for="bucket in types"
                            :key="bucket.type"
                        >
                            <td class="pa-0" style="height: 22px">
                                <v-checkbox
                                    v-model="bucket.checked"
                                    :label="bucket.type"
                                    @change="checkChange('type')"
                                    dense
                                    style="height: 22px"
                                    class="mt-0 pa-0"
                                />
                            </td>
                            <td class="pa-0 text-right">
                                {{bucket.doc_count}}
                            </td>
                        </tr>
                    </tbody>
                </v-simple-table>
            </v-card-text>
        </v-card>
        <v-card v-if="volumes.length" class="ma-3">
            <v-card-title class="h6 py-2">Volume</v-card-title>
            <v-card-text>
                <v-simple-table dense>
                    <tbody>
                        <tr v-for="bucket in volumes"
                            :key="bucket.volume"
                        >
                            <td class="pa-0" style="height: 22px">
                                <v-checkbox
                                    v-model="bucket.checked"
                                    :label="bucket.volume"
                                    @change="checkChange('volume')"
                                    dense
                                    style="height: 22px"
                                    class="mt-0 pa-0"
                                />
                            </td>
                            <td class="pa-0 text-right">
                                {{bucket.doc_count}}
                            </td>
                        </tr>
                    </tbody>
                </v-simple-table>
            </v-card-text>
        </v-card>
        <v-card v-if="books.length" class="ma-3">
            <v-card-title class="h6 py-2">Cărți</v-card-title>
            <v-card-text>
                <v-simple-table dense>
                    <tbody>
                        <tr v-for="bucket in books"
                            :key="bucket.book"
                        >
                            <td class="pa-0" style="height: 22px">
                                <v-checkbox
                                    v-model="bucket.checked"
                                    :label="bucket.book"
                                    @change="checkChange('book')"
                                    dense
                                    style="height: 22px"
                                    class="mt-0 pa-0"
                                />
                            </td>
                            <td class="pa-0 text-right">
                                {{bucket.doc_count}}
                            </td>
                        </tr>
                    </tbody>
                </v-simple-table>
            </v-card-text>
        </v-card>
    </div>
</template>
<script>

import shared from '~/components/Shared.vue';
import EventBus from '~/components/EventBus.vue';

export default {
	data() {
        return {
            authors: shared.authors,
            types: shared.types,
            volumes: shared.volumes,
            books: shared.books,
        }
    },
    methods: {
        checkChange(field) {
            EventBus.$emit('requery', field);
        },
    }
}
</script>