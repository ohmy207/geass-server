
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
            thread.initWeixin();

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
