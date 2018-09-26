


Vue.component('fenye',{

  props: { page: Object},
  template: ' <div v-if="page.page_count<=8">\n' +
      '          <ul  class="uk-pagination" >\n' +
      '             <li v-if="page.has_previous==1">\n' +
      '                   <a v-on:click="get_page(page.page_index-1)"> <i class="uk-icon-angle-double-left"></i></a>\n' +
      '             </li>\n' +
      '             <li uk="uk-disabled" v-else>\n' +
      '                   <span> <i class="uk-icon-angle-double-left"></i></span>\n' +
      '             </li>\n' +
      '             <template v-for="n in page.page_count">\n' +
      '                 <li v-if="n==page.page_index" class="uk-active">\n' +
      '                      <span v-text="n"></span>\n' +
      '                 </li>\n' +
      '                 <li v-else>\n' +
      '                      <a  v-on:click="get_page(n)" v-text="n"></a>\n' +
      '                 </li>\n' +
      '             </template>\n' +
      '\n' +
      '              <li v-if="page.has_next==1">\n' +
      '                   <a v-on:click="get_page(page.page_index+1)"> <i class="uk-icon-angle-double-right"></i></a>\n' +
      '             </li>\n' +
      '             <li uk="uk-disabled" v-else>\n' +
      '                   <span> <i class="uk-icon-angle-double-right"></i></span>\n' +
      '             </li>\n' +
      '          </ul>\n' +
      '        </div>\n' +
      '\n' +
      '\n' +
      '\n' +
      '\n' +
      '        <div v-else>\n' +
      '            <ul  class="uk-pagination" >\n' +
      '             <li v-if="page.has_previous==1">\n' +
      '                   <a v-on:click="get_page(page.page_index-1)"> <i class="uk-icon-angle-double-left"></i></a>\n' +
      '             </li>\n' +
      '             <li uk="uk-disabled" v-else>\n' +
      '                   <span> <i class="uk-icon-angle-double-left"></i></span>\n' +
      '             </li>\n' +
      '\n' +
      '                <li v-if="page.page_index==1" class="uk-active">\n' +
      '                      <span v-text="page.page_index"></span>\n' +
      '                 </li>\n' +
      '                 <li v-else>\n' +
      '                      <a  v-on:click="get_page(1)" v-text="1"></a>\n' +
      '                 </li>\n' +
      '                 <li>\n' +
      '                     <span>...</span>\n' +
      '                 </li>\n' +
      '\n' +
      '                <template v-if="page.page_index<=(page.page_count/2-1)">\n' +
      '                    <template v-if="page.page_index!=1">\n' +
      '                     <li  class="uk-active">\n' +
      '                         <span v-text="page.page_index"></span>\n' +
      '                      </li>\n' +
      '                     <li >\n' +
      '                         <a  v-on:click="get_page(page.page_index+1)" v-text="page.page_index+1"></a>\n' +
      '                     </li>\n' +
      '                    <li >\n' +
      '                        <a  v-on:click="get_page(page.page_index+2)" v-text="page.page_index+2"></a>\n' +
      '                    </li>\n' +
      '                    </template>\n' +
      '             </template>\n' +
      '             <template v-if="page.page_index>(page.page_count/2-1)">\n' +
      '                 <template v-if="page.page_index!=page.page_count">\n' +
      '                     <li >\n' +
      '                         <a  v-on:click="get_page(page.page_index-2)" v-text="page.page_index-2"></a>\n' +
      '                     </li>\n' +
      '                    <li >\n' +
      '                        <a  v-on:click="get_page(page.page_index-1)" v-text="page.page_index-1"></a>\n' +
      '                    </li>\n' +
      '                 <li  class="uk-active">\n' +
      '                     <span v-text="page.page_index"></span>\n' +
      '                 </li>\n' +
      '                 </template>\n' +
      '             </template>\n' +
      '\n' +
      '\n' +
      '              <template v-if="page.page_index==1">\n' +
      '                     <li >\n' +
      '                        <a  v-on:click="get_page(parseInt(page.page_count/2)-1)" v-text="parseInt(page.page_count/2)-1"></a>\n' +
      '                     </li>\n' +
      '                  <li >\n' +
      '                      <a  v-on:click="get_page(parseInt(page.page_count/2))" v-text="parseInt(page.page_count/2)"></a>\n' +
      '                  </li>\n' +
      '                  <li >\n' +
      '                      <a  v-on:click="get_page(parseInt(page.page_count/2)+1)" v-text="parseInt(page.page_count/2)+1"></a>\n' +
      '                  </li>\n' +
      '\n' +
      '              </template>\n' +
      '                    <template v-if="page.page_index==page.page_count">\n' +
      '                     <li >\n' +
      '                        <a  v-on:click="get_page(parseInt(page.page_count/2)-1)" v-text="parseInt(page.page_count/2)-1"></a>\n' +
      '                     </li>\n' +
      '                  <li >\n' +
      '                      <a  v-on:click="get_page(parseInt(page.page_count/2))" v-text="parseInt(page.page_count/2)"></a>\n' +
      '                  </li>\n' +
      '                  <li >\n' +
      '                      <a  v-on:click="get_page(parseInt(page.page_count/2)+1)" v-text="parseInt(page.page_count/2)+1"></a>\n' +
      '                  </li>\n' +
      '\n' +
      '              </template>\n' +
      '\n' +
      '\n' +
      '\n' +
      '\n' +
      '                 <li>\n' +
      '                     <span>...</span>\n' +
      '                 </li>\n' +
      '\n' +
      '                  <li v-if="page.page_index==page.page_count" class="uk-active">\n' +
      '                      <span v-text="page.page_count"></span>\n' +
      '                 </li>\n' +
      '                 <li v-else>\n' +
      '                      <a  v-on:click="get_page(page.page_count)" v-text="page.page_count"></a>\n' +
      '                 </li>\n' +
      '\n' +
      '                 <li v-if="page.has_next==1">\n' +
      '                   <a v-on:click="get_page(page.page_index+1)"> <i class="uk-icon-angle-double-right"></i></a>\n' +
      '             </li>\n' +
      '             <li uk="uk-disabled" v-else>\n' +
      '                   <span> <i class="uk-icon-angle-double-right"></i></span>\n' +
      '             </li>\n' +
      '\n' +
      '\n' +
      '            </ul>\n' +
      '        </div>',
     methods: {
         get_page: function (page_index) {
             alert('get_page function');
             location.assign('/?page_index=' + page_index);
         },
     }
});


