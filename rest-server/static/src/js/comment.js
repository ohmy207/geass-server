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
                url: '/' + window.coParent + '/' + window.parentId + '/comments',
                emptyCon: '',
                callback: exports.renderList,
            }, action);
        },

        // render data
        render: function(re, clear) {
            exports.renderList(re)

            if (re.data.topic) {
                thread.initWeixin({
                    title: re.data.topic.title,
                    desc: re.data.topic.content,
                    link: 'http://geass.me/topic?tid=' + re.data.topic.tid,
                    imgUrl: re.data.topic.picture_urls.length > 0 ? re.data.topic.picture_urls[0]['origin'] : '',
                });
            } else if (re.data.opinion) {
                thread.initWeixin({
                    title: re.data.opinion.topic_title,
                    desc: re.data.opinion.content,
                    link: 'http://geass.me/opinion?tid=' + re.data.opinion.tid + '&oid=' + re.data.opinion.oid,
                    imgUrl: re.data.opinion.picture_urls.length > 0 ? re.data.opinion.picture_urls[0]['origin'] : '',
                });
            } else {
                thread.initWeixin();
            }
        },

        renderList: function(re) {
            var allReplyHtml = template('tmpl_reply', re.data);
            if(jq.trim(allReplyHtml)!==''){
                //jq('#allLabelBox').show();
                jq('#allReplyList').css({height:'auto'})
                jq('#allReplyList').append(allReplyHtml);
            }
        },

        init: function() {
            var coParent = window.coParent,
                url = '/' + coParent + '/' + window.parentId + '/comments';

            thread.load({
                isList: false,
                isEmptyShow: true,
                url: '/' + window.coParent + '/' + window.parentId + '/comments?first=1&skip=0',
                emptyCon: '还没有任何评论',
                callback: exports.render,
            }, 'drag');

            initLazyload('.warp img');

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

            jq('.warp, #bottomBar').on('click', '.threadReply', function() {
                var thisObj = jq(this),
                    callback = function() {
                        thread.reply(url,  null, '', 'comment');
                    };
                thread.checkIsRegistered(callback);
            });

            jq('#allReplyList').on('click', '.commReply', function(e) {
                var thisObj = jq(this);
                if (thisObj.hasClass('unfold')) {
                    thisObj.attr('class', 'commReply');
                } else {
                    thisObj.attr('class', 'commReply unfold');
                }
            });

            // 回复
            jq('#allReplyList').on('click', '.replyFloor', function(e) {
                var thisObj = jq(this).parents('li');
                //var authorUId = thisObj.attr('uid');
                // 获取帖子id
                var divId = thisObj.attr('id'), author;

                var callback = function() {
                    if (/co_[0-9a-f]{24}/.test(divId)) {
                        if (match = divId.match(/co_([0-9a-f]{24})/)) {
                            toCoId = match[1];
                        }

                        e.stopPropagation();
                        jq.UTIL.touchStateNow(jq(this));

                        author = thisObj.attr('author');
                        thread.reply(url, toCoId, author, 'comment');
                    }
                };
                thread.checkIsRegistered(callback);
            });

            thread.initTouchRefresh(exports.load);

            // like
            jq('.topicCon .replyShare,#hotReplyList,#allReplyList').on('click', '.like', function(e) {
                jq.UTIL.touchStateNow(jq(this));
                e.stopPropagation();

                var thisObj = jq(this),
                    coId = thisObj.attr('coid') || null;

                var callback = function() {
                    if(thisObj.children('i').hasClass('iconPraise')) {
                        return;
                    }

                    var opts = {
                        'success': function(result) {
                            if (result.code == 0) {
                            //if (result.code == 0 && result.data && result.data.likeNum) {
                                //jq.UTIL.likeTips(thisObj, '+1');
                                thisObj.attr('class', 'like c13');
                                thisObj.html('<i class="iconPraise f18 cf"></i>' + (parseInt(thisObj.data('num')) + 1));
                            }
                        },
                        'noShowLoading' : true,
                        'noMsg' : true
                    }

                    var url = '/user/liking/' + coParent + '/comments/' + coId;
                    var data = {};

                    jq.UTIL.ajax(url, data, opts);
                };
                thread.checkIsRegistered(callback);
            });

            /**
             * @desc 全部回复加倒序查看
             * @param desc 为0是正序，为1时倒序
             */
            //var replySortBtn = jq('.evtReplySort'),
            //    replySortIcon = replySortBtn.find('i'),
            //    replySortSwitch = function () {
            //        if (!exports.desc) {
            //            replySortIcon.removeClass('iconSequence');
            //            replySortIcon.addClass('iconReverse');
            //            replySortBtn.html('倒序排列');
            //            replySortBtn.prepend(replySortIcon);
            //        } else {
            //            replySortIcon.removeClass('iconReverse');
            //            replySortIcon.addClass('iconSequence');
            //            replySortBtn.html('正序排列');
            //            replySortBtn.prepend(replySortIcon);
            //        }
            //    };
            //replySortSwitch();
            //replySortBtn.on('click', function () {
            //    var allReplyWrap = jq('#allReplyList'),
            //        allReplyHeight = allReplyWrap.height();
            //    allReplyWrap.css({height: allReplyHeight});
            //    allReplyWrap.html('');
            //    exports.nextStart = 0;
            //    exports.desc = !exports.desc ? 1 : 0;
            //    replySortSwitch();
            //    exports.load(exports.nextStart, 'sort');
            //    //pgvSendClick({hottag: 'wsq.reply.sort.inverse'});
            //});

        },

    };

    exports.init();

});
