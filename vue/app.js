import Vue from 'vue'
import { alert, modal } from 'vue-strap'
import Resource from './components/resource.vue' 

Vue.component('alert', alert);
Vue.component('modal', modal);
Vue.component('rdf-resource', Resource);

new Vue({
	el: '#v-app'
})