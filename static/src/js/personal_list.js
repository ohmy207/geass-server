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
        isLoadingNew: true,
        isLoading: false,
        isNoShowToTop: false,
        desc: 0,
        nextStart: 0,

        // load data,all in one
        load: function(start, action) {
            start = start || 0;
            action = action || '';

            exports.isLoading = true;
            /**
             * thread.js里调用，发表时新回复时，倒序，新发表的显示在最上面，正序在最下面
             */
            var desc = window.desc = exports.desc;
            var url = '/user/topics';

            if (window.listType == 'following') {
                url = '/user/following/topics';
            }

            url = url + '?skip=' + start;

            var opts = {
                'beforeSend': function() {
                    switch(action) {
                        case 'pull':
                            jq('#refreshWait').show();
                            jq('#showAll').hide();
                            exports.isLoadingNew = true;
                            break;
                        case 'drag':
                            jq('#loadNext').show();
                            exports.isLoadingNew = true;
                            break;
                        case 'sort':
                            jq('#showAll').hide();
                            exports.isLoadingNew = true;
                            jQuery.UTIL.showLoading();
                            break;
                        default:
                            jq.UTIL.showLoading();
                    }
                },
                'complete': function() {
                },
                'success': function(re) {
                    jq('#refreshWait').hide();
                    jq('#loadNext').hide();
                    jq.UTIL.showLoading('none');
                    if (re.code == 0) {
                        var zero = new Date;
                        exports.renderList(re, !start);
                        //stat.reportPoint('listRender', 10, new Date, zero);
                    } else {
                        jq.UTIL.dialog({content: '拉取数据失败，请重试', autoClose: true});
                    }
                    exports.isLoading = false;
                }
            };
            jq.UTIL.ajax(url, '', opts);
        },

        // render data
        renderList: function(re, clear) {
            if (clear) {
                jq('#list').html('');
            }

            // 最后无数据不再加载
            if (jq.UTIL.isObjectEmpty(re.data.dataList)) {
                exports.isLoadingNew = false;
                jq('#loadNext').hide();
                //jq('#showAll').show();
                if (clear) {
                    jq('.emptyList').html('还没有看法哦^…^').show()
                }
                return true;
            }
            //re.data.isWX = isWX;
            var tmplId = 'tmpl_' + (window.listType === 'news' ? 'newsList' : 'topicList');
            var listHtml = template(tmplId, re.data);

            jq('#list').append(listHtml);

            jq('#loadNext').hide();
            exports.nextStart = re.data.nextStart;

            //if (clear) {
            //    if (exports.order == 'hot') {
            //        jq('.badge').show();
            //    } else {
            //        jq('.badge').hide();
            //    }
            //}
        },

        init: function() {
            var tId = window.tId;

            exports.load(exports.nextStart, 'drag');

            initLazyload('.warp img');

            exports.nextStart = window.nextStart;

            var level = /Android 4.0/.test(window.navigator.userAgent) ? -10 : -100;
            // 全屏触摸
            jq.UTIL.initTouch({
                obj: jq('.warp')[0],
                end: function(e, offset) {
                    document.ontouchmove = function(e){ return true;}
                    var loadingObj = jq('#loadNext');
                    var loadingPos = jq('#loadNextPos');
                    // var loadingObjTop = loadingObj.offset().top + loadingObj.height() - jq(window).scrollTop();
                    var loadingObjTop = loadingPos.offset().top - document.body.scrollTop - window.screen.availHeight;
                    // 向上滑
                    if (offset.y > 10 && loadingObjTop <= 10 && exports.isLoadingNew && !exports.isLoading) {
                        exports.load(exports.nextStart, 'drag');
                    }
                    // 向下拉刷新
                    if (offset.y < level && document.body.scrollTop <= 0) {
                    }
                }
            });

            jq('.warp').on('click', '.topicWrap', function(e) {
                jq.UTIL.touchStateNow(jq(this).parent('li'));
                jq.UTIL.reload(jq(this).data('link'));
            });

        },

    };

    exports.init();

});
