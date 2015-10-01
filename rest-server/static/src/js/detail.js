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
        hasVoted: false,
        isLoadingFirst: true,

        load: function(action) {
            var url = '/topics/' + window.tId,
                isLoadingFirst = exports.isLoadingFirst;

            thread.load({
                isList: !isLoadingFirst,
                isEmptyShow: false,
                url: isLoadingFirst ? url : url + '/opinions',
                emptyCon: '',
                callback: isLoadingFirst ? exports.render : exports.renderList,
            }, action);
        },

        // render data
        render: function(re) {
            window.isLZ = re.data.is_lz || false;
            window.voteTotalNum = re.data.vote_total_num || 0;
            exports.hasVoted = re.data.has_user_voted || false;

            var topicHtml = template('tmpl_topic', re.data);
                is_topic_followed = re.data.is_topic_followed || false,
                follow_class = is_topic_followed ? 'followBtn followed f14 c2 fr' : 'followBtn f14 c2 fr',
                follow_html = is_topic_followed ? '已关注' : '关注';

            jq('.detailBox').prepend(topicHtml);
            jq('.topicInfo .followBtn').attr('class', follow_class).html(follow_html);
            jq('.topicInfo span').html('参与 ' + window.voteTotalNum + ' 人');
            jq('#bottomBar .iconReply').html(re.data.comments_count);

            var ReplyHtml = template('tmpl_proposals', {
                'data_list': re.data.proposal_list,
            });

            if(jq.trim(ReplyHtml)!==''){
                //jq('#allLabelBox').show();
                jq('#hotReplyList').append(ReplyHtml);
                jq('#hotReplyList').css({height:'auto'});

                thread.resetOpbar();
            }

            exports.renderList(re)

            jq('.warp, #bottomBar').show();

            exports.isLoadingFirst = false;
        },

        renderList: function(re) {
            var ReplyHtml = template('tmpl_opinions', re.data);
            if(jq.trim(ReplyHtml)!==''){
                jq('#allLabelBox').show();
                jq('#allReplyList').css({height:'auto'})
                jq('#allReplyList').append(ReplyHtml);
            }
        },

        init: function() {
            var tId = window.tId;

            // 分享遮罩，一次性
            //var action = jq.UTIL.getQuery('action');
            //var reapp = /qqdownloader\/([^\s]+)/i;

            exports.load('drag');

            initLazyload('.warp img');
            initLazyload('#opinionList img');

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
            //            jq('.gMask').on('click', function() {
            //                jq.UTIL.dialog({id:'shareMask'});
            //            });
            //            jq('#showShare').on('click', function() {
            //                jq(this).hide();
            //            });
            //        }
            //    });
            //    localStorage.setItem('hadShowShareMask', 1);
            //}

            // 点击查看大图
            //require.async('module/imageviewCommon', function(imageviewCommon) {
            //    imageviewCommon.init('.slideShow li');
            //    imageviewCommon.init('.threadPic span');
            //    imageviewCommon.init('.replyImg dd');
            //    // imageviewCommon.init('.slideBox li');
            //});

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

            // 主题和底部bar 帖点击回复
            jq('.topicBtn').on('click', '.threadReply', function() {
                var thisObj = jq(this),
                    callback = function() {
                        var replyType = thisObj.data('type');
                        thread.reply(tId, null, null, '', replyType);
                    };
                jq.UTIL.touchStateNow(thisObj);
                thread.checkIsRegistered(callback);
            });

            thread.initTouchRefresh(exports.load);

            jq('#hotReplyList,#allReplyList').on('click', '.proposalWrap, .opinionWrap', function(e) {
                var thisObj = jq(this), link;
                jq.UTIL.touchStateNow(thisObj.parent('li'));

                link = thisObj.attr('data-link') || '';
                if (link) {
                    jq.UTIL.reload(link);
                }
                return false;
            });

            jq('.topicTit').on('click', 'a', function(e) {
                jq.UTIL.touchStateNow(jq(this));
                jq.UTIL.reload('/proposal_list' + '?tid=' + tId);
            });

            // follow
            jq('.topicInfo').on('click', '.followBtn', function(e) {

                jq.UTIL.touchStateNow(jq(this));
                e.stopPropagation();

                var thisObj = jq(this),
                    tId = window.tId || null,
                    isFollowed = thisObj.hasClass('followed');

                var opts = {
                    'noShowLoading' : true,
                    'noMsg' : true
                };

                var url = '/user/following/topics',
                    data = {'tid':tId};

                var callback = function() {
                    if (isFollowed) {
                        opts.success = function(result) {
                            if (result.code == 0) {
                                thisObj.attr('class', 'followBtn f14 c2 fr');
                                thisObj.html('关注');
                            }
                        };

                        jq.UTIL.ajax(url, data, opts, 'DELETE');
                    } else {
                        opts.success = function(result) {
                            if (result.code == 0) {
                                thisObj.attr('class', 'followBtn followed f14 c2 fr');
                                thisObj.html('已关注')
                            }
                        };
                        jq.UTIL.ajax(url, data, opts);
                    }
                };
                thread.checkIsRegistered(callback);
            });

            // vote
            jq('#hotReplyList').on('click', '.vote', function(e) {

                jq.UTIL.touchStateNow(jq(this));
                e.stopPropagation();

                var thisObj = jq(this),
                    pId = thisObj.attr('pId') || null,
                    isVoted = thisObj.hasClass('voted'),
                    resultNum = parseInt(thisObj.data('num')) + 1,
                    resultClass = "voteCount voted vote",
                    //likeTips = "+1",
                    hasVoted = true,
                    url = '/user/vote/proposals',
                    data = {'tid':tId, 'pid': pId},
                    voteTotalNum = window.voteTotalNum + 1;

                var callback = function() {
                    if(isVoted && exports.hasVoted) {
                        resultNum = parseInt(thisObj.data('num')) - 1;
                        resultClass = "voteCount vote";
                        //likeTips = "-1";
                        hasVoted = false;
                        url = '/user/unvote/proposals';
                        voteTotalNum = window.voteTotalNum - 1;
                    }

                    var opts = {
                        'success': function(result) {
                            if (result.code == 0) {
                                exports.hasVoted = hasVoted;
                                //jq.UTIL.likeTips(thisObj, likeTips);
                                thisObj.attr('class', resultClass);
                                thisObj.html(resultNum);
                                thisObj.data('num', resultNum);
                                window.voteTotalNum = voteTotalNum;
                                thread.resetOpbar();
                            }
                        },
                        'noShowLoading' : true,
                        'noMsg' : true
                    }

                    if (!isVoted && exports.hasVoted) {
                        var dialogOpts = {
                            'id':'operationConfirm',
                            'isMask':true,
                            'content':'要取消之前的投票重新选择吗?',
                            'okValue':'确定',
                            'cancelValue':'取消',
                            'ok':function() {
                                opts.success = function(result) {
                                    if (result.code == 0) {
                                        var votedObj = jq('.voted');
                                        oldVoteNum = parseInt(votedObj.data('num'));
                                        votedObj.attr('class', 'voteCount vote');
                                        votedObj.html(oldVoteNum - 1);
                                        votedObj.data('num', oldVoteNum - 1);

                                        //jq.UTIL.likeTips(thisObj, likeTips);
                                        thisObj.attr('class', resultClass);
                                        thisObj.html(resultNum);
                                        thisObj.data('num', resultNum);

                                        thread.resetOpbar();
                                    }
                                },

                                url = '/user/revote/proposals';
                                jq.UTIL.ajax(url, data, opts);
                            },
                        };
                        jq.UTIL.dialog(dialogOpts);

                    } else {
                        jq.UTIL.ajax(url, data, opts);
                    }
                };
                thread.checkIsRegistered(callback);
            });

        },

    };

    exports.init();

});
