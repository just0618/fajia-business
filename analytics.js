/*
 * 法嘉商务网站 · 腾讯云 RUM 自定义行为统计
 *
 * 基础 PV / UV 由腾讯云 Aegis SDK 自动统计。
 * 本文件仅补充业务行为：PDF 下载、视频播放进度、BGM、外链、邮箱等。
 * 为控制上报量：同一页面会话内，每个视频的“首次播放”和每个进度节点只上报一次。
 */
(function () {
  'use strict';

  function cleanText(value, maxLength) {
    var text = String(value || '').replace(/\s+/g, ' ').trim();
    return text.slice(0, maxLength || 80);
  }

  function report(name, ext1, ext2, ext3) {
    var aegis = window.fajiaAegis;
    if (!aegis || typeof aegis.reportEvent !== 'function') return;

    try {
      aegis.reportEvent({
        name: cleanText(name, 60),
        ext1: cleanText(ext1, 100),
        ext2: cleanText(ext2, 100),
        ext3: cleanText(ext3, 100)
      });
    } catch (error) {
      // 统计失败不能阻断页面交互。
    }
  }

  function getSectionName(element) {
    var section = element && element.closest ? element.closest('section[id]') : null;
    return section ? section.id : 'page';
  }

  function getCardLabel(element) {
    if (!element || !element.closest) return '';

    var card = element.closest(
      '.work-catalog-card, .social-profile-card, .embedded-video-card, .brand-project, ' +
      '.weibo-static-card, .v-feature-card, .solo-editorial-panel, .event-feature-card, figure, article'
    );

    if (card) {
      var heading = card.querySelector('h4, h3, h2, figcaption');
      if (heading) return cleanText(heading.textContent, 80);
    }

    return cleanText(element.getAttribute && element.getAttribute('aria-label'), 80) ||
      cleanText(element.textContent, 80) ||
      cleanText(element.getAttribute && element.getAttribute('alt'), 80);
  }

  function sourceBasename(media) {
    var source = media && media.querySelector ? media.querySelector('source[src]') : null;
    var src = source ? source.getAttribute('src') : (media && media.getAttribute ? media.getAttribute('src') : '');
    if (!src) return '';
    return src.split('?')[0].split('#')[0].split('/').pop() || src;
  }

  function platformFromUrl(url) {
    var host = (url.hostname || '').toLowerCase();
    if (host === 'weibo.com' || host.endsWith('.weibo.com')) return '微博';
    if (host === 'douyin.com' || host.endsWith('.douyin.com')) return '抖音';
    if (host === 'xiaohongshu.com' || host.endsWith('.xiaohongshu.com') || host === 'xhslink.cn' || host.endsWith('.xhslink.cn')) return '小红书';
    if (host === 'instagram.com' || host.endsWith('.instagram.com')) return 'Instagram';
    if (host === 'qq.com' || host.endsWith('.qq.com')) return 'QQ音乐';
    if (host === 'youtube.com' || host.endsWith('.youtube.com') || host === 'youtu.be') return 'YouTube';
    if (host === 'jd.com' || host.endsWith('.jd.com')) return '京东';
    return host || '其他外链';
  }

  function bindPdfAndLinks() {
    document.addEventListener('click', function (event) {
      var target = event.target;
      if (!target || !target.closest) return;

      var copyButton = target.closest('#copyEmail');
      if (copyButton) {
        report('复制邮箱', 'mejoymedia@foxmail.com', 'contact', 'button');
        return;
      }

      var link = target.closest('a[href]');
      if (!link) return;

      var rawHref = link.getAttribute('href') || '';
      var label = getCardLabel(link) || cleanText(link.textContent, 80);
      var section = getSectionName(link);

      if (/\.pdf(?:$|[?#])/i.test(rawHref) || link.classList.contains('pdf-download')) {
        report('PDF下载', label || '下载最新版 PDF', section, rawHref.split('?')[0]);
        return;
      }

      if (/^mailto:/i.test(rawHref)) {
        report('联系邮箱', 'mejoymedia@foxmail.com', section, 'mailto');
        return;
      }

      try {
        var destination = new URL(rawHref, window.location.href);
        if ((destination.protocol === 'http:' || destination.protocol === 'https:') && destination.origin !== window.location.origin) {
          report('外链点击', platformFromUrl(destination), label, section);
        }
      } catch (error) {
        // 非标准链接无需统计。
      }
    }, true);
  }

  function bindVideos() {
    var videos = Array.prototype.slice.call(document.querySelectorAll('video'));

    videos.forEach(function (video) {
      var label = getCardLabel(video) || sourceBasename(video) || '未命名视频';
      var source = sourceBasename(video);
      var section = getSectionName(video);
      var started = false;
      var milestones = { 25: false, 50: false, 75: false };
      var completed = false;

      video.addEventListener('play', function () {
        if (started) return;
        started = true;
        report('视频播放', label, source, section);
      });

      video.addEventListener('timeupdate', function () {
        if (!Number.isFinite(video.duration) || video.duration <= 0) return;
        var percent = (video.currentTime / video.duration) * 100;

        [25, 50, 75].forEach(function (point) {
          if (!milestones[point] && percent >= point) {
            milestones[point] = true;
            report('视频' + point + '%', label, source, section);
          }
        });
      });

      video.addEventListener('ended', function () {
        if (completed) return;
        completed = true;
        report('视频完播', label, source, section);
      });
    });
  }

  function bindBgm() {
    var bgm = document.getElementById('siteBgm');
    if (!bgm) return;

    var started = false;
    bgm.addEventListener('play', function () {
      if (started) return;
      started = true;
      report('BGM播放', '《小英雄》', sourceBasename(bgm), 'music-player');
    });
  }

  function init() {
    bindPdfAndLinks();
    bindVideos();
    bindBgm();

    // 便于以后新增特定按钮时复用，不包含任何用户身份信息。
    window.fajiaAnalytics = {
      report: report
    };
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init, { once: true });
  } else {
    init();
  }
})();
