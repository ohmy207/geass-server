/**
 **/

require.config({

    waitSeconds: 15,
    urlArgs: "t=" + (new Date()).getTime(),

    paths: {

        //"jquery": "vendor/jquery-1.11.2.min",
        "jquery": "vendor/jquery.min",
        "art-template": "vendor/art-template",
        "util": "module/util",

        "jpegMeta": "module/jpegMeta",
        "JPEGEncoder": "module/JPEGEncoder",
        "imageCompresser": "module/imageCompresser",
        "uploadImg": "module/uploadImg",
        "thread": "module/thread",
    }

});

require(['art-template', 'util', 'thread'],function (template, util, thread){

    var exports = {

        load: function(action) {
            var emptyCons = {
                'publish_opinions': '还没有发表过看法',
                'publish_topics': '还没有发表过话题',
                'following': '还没有任何关注',
            };

            var urlMap = {
                'publish_opinions': 'opinions',
                'publish_topics': 'topics',
                'following': 'following',
            };

            thread.load({
                isList: true,
                isEmptyShow: true,
                url: '/user/' + urlMap[window.listType],
                emptyCon: emptyCons[window.listType],
                callback: exports.renderList,
            }, action);
        },

        // render data
        renderList: function(re) {
            var tmplId = window.listType === 'publish_opinions' ? 'tmpl_opinionList' : 'tmpl_topicList';
            var listHtml = template(tmplId, re.data);
            jq('#list').append(listHtml);
        },

        init: function() {
            var tId = window.tId;

            exports.load('drag');

            initLazyload('.warp img');

            thread.initTouchRefresh(exports.load);

            jq('.warp').on('click', '.topicWrap', function(e) {
                jq.UTIL.touchStateNow(jq(this).parent('li'));
                jq.UTIL.reload(jq(this).data('link'));
            });

        },

    };

    exports.init();

});
