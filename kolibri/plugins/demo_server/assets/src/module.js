import Vue from 'kolibri.lib.vue';
import DemoServerIndex from './views/DemoServerIndex';
import KolibriModule from 'kolibri_module';

class DemoServerModule extends KolibriModule {
  ready() {
    const modalDiv = global.document.createElement('div');
    global.document.body.appendChild(modalDiv);
    this.rootvue = new Vue(Object.assign({ el: modalDiv }, DemoServerIndex));
  }
}

export default new DemoServerModule();
