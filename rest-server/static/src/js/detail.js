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
        //moreType: 'more',
        nextStart: 5,
        //startPos: 0,

        load: function(action) {
            thread.load({
                isList: true,
                isEmptyShow: false,
                url: '/topics/' + window.tId + '/opinions',
                emptyCon: '',
                callback: exports.renderList,
            }, action);
        },

        // render data
        render: function(re, clear) {
            exports.hasVoted = re.data.has_user_voted || false;

            var topicHtml = template('tmpl_topic', re.data);
                is_topic_followed = re.data.is_topic_followed || false,
                follow_class = is_topic_followed ? 'followBtn followed f14 c2 fr' : 'followBtn f14 c2 fr',
                follow_html = is_topic_followed ? '已关注' : '关注';

            jq('.detailBox').prepend(topicHtml);
            exports.renderProposals(re, clear)
            exports.renderList(re)

            if (re.data.has_opinion) {
                jq('.topicBtn').find('[data-type="opinion"]').html('<i class="iconReply2 f18 cf cc"></i>已发表看法').addClass('hasReply')
            }
            jq('.topicInfo .followBtn').attr('class', follow_class).html(follow_html);
            //jq('.topicInfo .iconTotal').after(thread.voteTotalNum + ' 票');
            jq('#bottomBar .iconReply').parent('.item').html('<i class="cf iconReply"></i>' + re.data.comments_count);

            jq('.warp, #bottomBar').show();

            exports.isAnonymous = re.data.topic.is_anonymous || false;
            exports.isAuthor = re.data.is_author || false;
            thread.initWeixin({
                title: re.data.topic.title,
                desc: re.data.topic.content,
                imgUrl: re.data.topic.picture_urls.length > 0 ? re.data.topic.picture_urls[0]['origin'] : jq('.proposaList img').first().data('src'),
            });
        },

        renderProposals: function(re, clear) {

            if (re.data.has_more_proposals) {
                //if (exports.moreType === 'all') {
                //    jq('.loadMore span').html('显示全部选项');
                //}
                jq('.loadMore').show();
            } else {
                jq('.loadMore').hide();
            }

            thread.voteTotalNum = re.data.vote_total_num || 0;
            //re.data.startPos = exports.startPos;
            re.data.startPos = clear ? 0 : exports.nextStart;
            re.data.colorList = thread.colorList;

            var listHtml = template('tmpl_proposals', re.data);
            if(jq.trim(listHtml)!==''){
                //jq('#allLabelBox').show();
                jq('#hotReplyList').append(listHtml);
                jq('#hotReplyList').css({height:'auto'});
                thread.resetAllOpbar();
            }

            if (!clear && re.data.next_start) {
                exports.nextStart = re.data.next_start;
            }
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
                loadOpts = {
                    isList: false,
                    isEmptyShow: false,
                    url: '/topics/' + tId,
                    emptyCon: '',
                    callback: exports.render,
                };

            thread.load(loadOpts, 'drag');
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

            // 点击查看大图
            jq('.warp').on('click', '.threadPic img', function() {
                var thisObj = jq(this),
                    current = thisObj.data('origin'),
                    urls = [];

                jq('.threadPic img').each(function() {
                    urls.push(jq(this).data('origin'));
                });

                wx.previewImage({
                    current: current,
                    urls: urls
                });
            });

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

            jq('.topicBtn').on('click', '.threadReply', function() {
                var thisObj = jq(this);
                jq.UTIL.touchStateNow(thisObj);

                if (thisObj.hasClass('hasReply')) {
                    return false;
                }

                thread.checkIsRegistered(function() {
                    var formType = thisObj.data('type'),
                        url = formType == 'proposal' ? '/topics/'+tId+'/proposals' : '/topics/'+tId+'/opinions'
                    thread.reply(url, null, '', formType);
                });
            });

            jq('.topicInfo').on('click', '.threadEdit', function() {
                var callback = function() {
                    thread.edit(loadOpts.url, 'topic', exports.isAnonymous, exports.isAuthor);
                };
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

            jq('.warp').on('click', '.loadMore', function(e) {
                jq.UTIL.touchStateNow(jq(this));

                var loadOpts = {
                    isList: true,
                    isEmptyShow: false,
                    url: '/topics/' + tId + '/proposals',
                    emptyCon: '',
                    //type: exports.moreType,
                    nextStart: exports.nextStart,
                    isNextStartUpdate: false,
                    callback: exports.renderProposals,
                };

                //if (exports.moreType === 'all') {
                //    exports.startPos = 15;
                //} else if (exports.moreType === 'more') {
                //    exports.startPos = 5;
                //    exports.moreType = 'all';
                //}
                thread.load(loadOpts, 'more');
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

                var url = '/user/following/topics/' + tId,
                    data = {};

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
                    resultStyle = {'background': thisObj.parent('.opWrap').find('.oppi').css('color')},
                    //likeTips = "+1",
                    hasVoted = true,
                    url = '/user/voting/proposals/' + pId,
                    ajaxType = 'POST',
                    data = {},
                    voteTotalNum = thread.voteTotalNum + 1;

                var callback = function() {
                    if(isVoted && exports.hasVoted) {
                        resultNum = parseInt(thisObj.data('num')) - 1;
                        resultClass = "voteCount vote";
                        resultStyle = {'background': ''};
                        //likeTips = "-1";
                        hasVoted = false;
                        ajaxType = 'DELETE';
                        voteTotalNum = thread.voteTotalNum - 1;
                    }

                    var opts = {
                        'success': function(result) {
                            if (result.code == 0) {
                                exports.hasVoted = hasVoted;
                                //jq.UTIL.likeTips(thisObj, likeTips);
                                thisObj.attr('class', resultClass);
                                thisObj.css(resultStyle);
                                thisObj.html(resultNum);
                                thisObj.data('num', resultNum);
                                thread.voteTotalNum = voteTotalNum;
                                thread.resetAllOpbar();
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
                                        votedObj.css({'background': ''});
                                        votedObj.html(oldVoteNum - 1);
                                        votedObj.data('num', oldVoteNum - 1);

                                        //jq.UTIL.likeTips(thisObj, likeTips);
                                        thisObj.attr('class', resultClass);
                                        thisObj.css(resultStyle);
                                        thisObj.html(resultNum);
                                        thisObj.data('num', resultNum);

                                        thread.resetAllOpbar();
                                    }
                                },

                                jq.UTIL.ajax(url, data, opts, 'PATCH');
                            },
                        };
                        jq.UTIL.dialog(dialogOpts);

                    } else {
                        jq.UTIL.ajax(url, data, opts, ajaxType);
                    }
                };
                thread.checkIsRegistered(callback);
            });

        },

    };

    exports.init();

});
