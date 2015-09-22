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
                'publish_opinions': '还没有发表话题！',
                'publish_topics': '还没有发表话题！',
                'following': '还没有关注话题！',
            };

            var urlMap = {
                'publish_opinions': 'publishing/opinions',
                'publish_topics': 'publishing/topics',
                'following': 'following/topics',
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
