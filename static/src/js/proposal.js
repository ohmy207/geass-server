/**
 * @filename main
 * @description
 * 作者: xuguangzhou
 * 创建时间: 2015-03-24 20:01:03
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
            var url = '/p/' + window.pId;

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
            var proposalHtml = template('tmpl_proposal', re.data);
            jq('.warp').prepend(proposalHtml);

            exports.isLoadingFirst = false;
            jq('.warp, #bottomBar').show()
            //jq('.warp, #bottomBar, .recommendTitle').show()
        },

        init: function() {
            var tId = window.tId;
            var parentId = window.parentId || 0;

            // 分享遮罩，一次性
            //var action = jq.UTIL.getQuery('action');
            //var reapp = /qqdownloader\/([^\s]+)/i;

            exports.load('drag');
            //var jsonData = parseJSON(window.jsonData);
            //exports.renderList({data: jsonData}, true);
            //g_ts.first_render_end = new Date();

            initLazyload('.warp img');

            // appbar no share mask
            //if (action == 'share' && !reapp.test(navigator.userAgent)) {
            //    var hadShowShareMask = localStorage.getItem('hadShowShareMask'),
            //        isMask = false;
            //    if (!hadShowShareMask) {
            //        isMask = true;
            //    }
            //    var tmpl = template.render('tmpl_pageTip', {'msg':'喜欢这个话题，请点击右上角图标分享'});
            //    jq.UTIL.dialog({
            //        id: 'shareMask',
            //        top:0,
            //        content: tmpl,
            //        isHtml: true,
            //        isMask: isMask,
            //        callback: function() {
            //            jq('.g-mask').on('click', function() {
            //                jq.UTIL.dialog({id:'shareMask'});
            //            });
            //            jq('#showShare').on('click', function() {
            //                jq(this).hide();
            //            });
            //        }
            //    });
            //    localStorage.setItem('hadShowShareMask', 1);
            //}

            // 主题和底部bar 帖点击回复
            //jq.UTIL.touchState('.threadReply', 'commBg', '.warp');
            //jq.UTIL.touchState('.threadReply', 'commBg', '#bottomBar');
            jq('.warp, #bottomBar').on('click', '.threadReply', function() {
                var thisObj = jq(this);
                //thread.reply(tId, parentId, '', 'proposal');
                thread.reply(tId, null, '', 'proposal');
            });

            jq('.warp').on('click', '.detail', function(e) {
                jq.UTIL.touchStateNow(jq(this), 'tapBg1');
                jq.UTIL.reload(jq(this).data('link'));
            });

            // like
            jq('.topicCon .replyShare,#hotReplyList,#allReplyList').on('click', '.like', function(e) {
                jq.UTIL.touchStateNow(jq(this));
                e.stopPropagation();

                var thisObj = jq(this),
                    pId = thisObj.attr('pId') || 0;
                if(thisObj.children('i').hasClass('iconPraise')) {
                    return;
                }

                // 晒图结束不能定
                if (parentId && thisObj.attr('isEnd') == 1 && !pId) {
                    jq.UTIL.dialog({content: '活动已结束，请不要再赞了', autoClose: true});
                    return false;
                }

                var opts = {
                    'success': function(result) {
                        if (result.code == 0 && result.data && result.data.voteNum) {
                            //if (parentId > 0 && !pId) {
                            jq.UTIL.likeTips(thisObj, '+1');
                            //}
                            //thisObj.html('<i class="iconPraise f18 cf"></i>' + '<span class="readNumText">' + result.data.voteNum + '</span>');
                            thisObj.attr('class', 'voteCount voted like');
                            thisObj.html(result.data.voteNum)
                            // 赞的不是回复时
                            //if (!pId) {
                            //    //移除掉blur遮罩
                            //    jq('.blur').each(function(obj){
                            //        if(jq(this).attr('alt') == tId){
                            //            jq(this).removeClass();
                            //        }
                            //    });
                            //    jq('.slideText').each(function(obj){
                            //        if(jq(this).attr('alt') == tId){
                            //            jq(this).css('display', 'none');
                            //        }
                            //    });
                            //}
                            //if (isWX && isWeixinLink && jq.UTIL.getQuery('source')) {
                            //    wxFollow.wxFollowTips();
                            //}
                        }
                    },
                    'noShowLoading' : true,
                    'noMsg' : true
                }

                var url = '/p/vote';
                var data = {'tid':tId, 'pid': pId};
                //var url = '/' + sId;
                //var data = {'tId':tId, 'parentId': parentId, 'CSRFToken':CSRFToken};
                //if (pId) {
                //    url = url + '/r/like';
                //    data.pId = pId;
                //} else {
                //    url = url + '/like';
                //}

                jq.UTIL.ajax(url, data, opts);
            });

        },

    };

    exports.init();

});
