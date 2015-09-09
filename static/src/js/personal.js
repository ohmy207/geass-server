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
        isLoadingFirst: true,
        isLoading: false,
        isNoShowToTop: false,
        hasVoted: false,
        desc: 0,
        nextStart: 0,

        // load data,all in one
        load: function(action) {
            action = action || '';

            exports.isLoading = true;
            /**
             * thread.js里调用，发表时新回复时，倒序，新发表的显示在最上面，正序在最下面
             */
            var desc = window.desc = exports.desc;
            //var url = DOMAIN + window.sId + '/t/' + window.tId
            var url = '/user';// + window.pId;

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
                        exports.render(re);
                    } else {
                        jq.UTIL.dialog({content: '拉取数据失败，请重试', autoClose: true});
                    }
                    exports.isLoading = false;
                }
            };
            jq.UTIL.ajax(url, '', opts);
        },

        // render data
        render: function(re) {
            //jq('html, body, #loadNext').css('background-color', '#ebebeb')
            //jq('html, body').css('background-color', '#f3f3f3')

            var followHtml = template('tmpl_topicList', {'dataList': re.data.follow.data_list, 'count': re.data.follow.count, 'title': '我的关注', 'link': '/following'}),
                headerHtml = template('tmpl_header', re.data),
                publishHtml = template('tmpl_topicList', {'dataList': re.data.publish.data_list, 'count': re.data.publish.count, 'title': '发表的话题', 'link': '/publishing'});

            jq('#header').append(headerHtml);
            jq('#follow').append(followHtml);
            jq('#publish').append(publishHtml);

            exports.isLoadingFirst = false;
            jq('.warp').show()
            //jq('.warp, #bottomBar').show()
            //jq('.warp, #bottomBar, .recommendTitle').show()

            exports.hasVoted = re.data.has_voted || false;
        },

        init: function() {
            var tId = window.tId;
            var parentId = window.parentId || 0;

            exports.load('drag');

            initLazyload('.warp img');

            jq('.warp, #bottomBar').on('click', '.threadReply', function() {
                var thisObj = jq(this);
                //thread.reply(tId, parentId, '', 'proposal');
                thread.reply(tId, null, '', 'proposal');
            });

            jq('.warp').on('click', '.pTitle', function(e) {
                jq.UTIL.touchStateNow(jq(this));
                jq.UTIL.reload(jq(this).data('link'));
            });

            jq('.warp').on('click', '.topicWrap', function(e) {
                jq.UTIL.touchStateNow(jq(this).parent('li'));
                jq.UTIL.reload(jq(this).data('link'));
            });

        },

    };

    exports.init();

});
