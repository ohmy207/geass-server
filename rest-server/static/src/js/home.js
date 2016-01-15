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
            thread.load({
                isList: true,
                isEmptyShow: false,
                url: '/topics',
                emptyCon: '',
                callback: exports.renderList,
            }, action);
        },

        // render data
        render: function(re, clear) {

            exports.renderList(re)
            jq('.warp, .publishBar').show();

            thread.initWeixin({
                title: 'There - 投票社区',
                desc: 'There 是一个社区化的数据调查平台，在这里用户可以温和地表达自己的意愿和态度，分享彼此的看法和见解。通过数据分析，There 能够帮助展示分歧和意见分布，促进达成共识，为中文互联网提供有价值的参考数据。',
            });
        },

        renderList: function(re) {
            var topicsHtml = template('tmpl_topicList', re.data);
            if(jq.trim(topicsHtml)!==''){
                jq('#topicList').append(topicsHtml);
            }
        },

        init: function() {

            thread.load({
                isList: true,
                isEmptyShow: false,
                url: '/topics',
                emptyCon: '',
                callback: exports.render,
            }, 'drag');

            initLazyload('.warp img');

            //var action = jq.UTIL.getQuery('action');
            //var hadShowGuide = localStorage.getItem('hadShowGuide')

            //if (!hadShowGuide) {
            //    var tmpl = template('tmpl_pageGuide', {'msg':'可以从个人页关注There 公众号'});
            //    jq.UTIL.dialog({
            //        id: 'guideMask',
            //        top:0,
            //        content: tmpl,
            //        isHtml: true,
            //        isMask: true,
            //        callback: function() {
            //            jq('.gMask').on('click', function() {
            //                jq.UTIL.dialog({id:'guideMask'});
            //            });
            //            //jq('#showShare').on('click', function() {
            //            //    jq(this).hide();
            //            //});
            //        }
            //    });
            //    localStorage.setItem('hadShowGuide', 1);
            //}

            //setInterval(function() {
            //    if (window.pageYOffset > 1000 && !thread.isNoShowToTop) {
            //        jq('#goTop').show();
            //    } else {
            //        jq('#goTop').hide();
            //    }

            //}, 200);

            //jq('.upBtn').on('click', function() {
            //    jq('#goTop').hide();
            //    scroll(0,0);
            //});

            thread.initTouchRefresh(exports.load);

            jq('.homeList').on('click', '.topicTitle, .textContainer, .imgContainer', function(e) {
                var thisObj = jq(this), link;

                jq.UTIL.touchStateNow(thisObj);
                link = thisObj.hasClass('topicTitle') ? thisObj.attr('data-link') : thisObj.find('.listContent').attr('data-link');

                if (link) {
                    jq.UTIL.reload(link);
                }
                return false;
            });

        },

    };

    exports.init();

});
