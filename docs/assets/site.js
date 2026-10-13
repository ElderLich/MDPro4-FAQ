'use strict';
(() => {
  const data = JSON.parse(document.getElementById('faq-data').textContent);
  const $ = id => document.getElementById(id);
  const answers = [...document.querySelectorAll('#answers > details')];
  const byId = new Map(data.faqs.map(faq => [faq.id, faq]));
  const normalize = value => value.normalize('NFKD').replace(/[\u0300-\u036f]/g, '').toLocaleLowerCase();
  const searchable = new Map(data.faqs.map(faq => [faq.id, normalize(faq.title + ' ' + faq.body)]));
  let category = 'all';
  let toastTimer;

  function showSection(name) {
    document.querySelectorAll('[data-section]').forEach(section => { section.hidden = section.dataset.section !== name; });
    document.querySelectorAll('[data-pane]').forEach(link => {
      if (link.dataset.pane === name) link.setAttribute('aria-current', 'page');
      else link.removeAttribute('aria-current');
    });
  }

  function filter() {
    const query = $('search').value.trim();
    const terms = normalize(query).split(/\s+/).filter(Boolean);
    let count = 0;
    answers.forEach(answer => {
      const match = (category === 'all' || answer.dataset.category === category) && terms.every(term => searchable.get(answer.id.slice(4)).includes(term));
      answer.hidden = !match;
      if (match) count++;
    });
    document.querySelectorAll('[data-category].category-button').forEach(button => button.setAttribute('aria-pressed', String(button.dataset.category === category)));
    $('results-title').textContent = category === 'all' ? 'All answers' : data.categories.find(item => item.id === category).title;
    $('result-count').textContent = `${count} ${count === 1 ? 'answer' : 'answers'}${query ? ` matching “${query}”` : ' · Select a question to read more'}`;
    $('empty').hidden = count !== 0;
    $('clear-search').hidden = !query;
    $('search-key').hidden = !!query;
    $('expand-all').disabled = $('collapse-all').disabled = count === 0;
  }

  function route() {
    const hash = location.hash.slice(1);
    if (hash.startsWith('faq-') && byId.has(hash.slice(4))) {
      category = 'all';
      $('search').value = '';
      showSection('faq');
      filter();
      const answer = $(hash);
      answer.open = true;
      answer.scrollIntoView({block: 'start'});
    } else if (hash.startsWith('category-') && data.categories.some(item => item.id === hash.slice(9))) {
      category = hash.slice(9);
      $('search').value = '';
      showSection('faq');
      filter();
      $('faq').scrollIntoView({block: 'start'});
    } else {
      showSection(hash === 'support' || hash === 'resources' ? hash : 'faq');
      if (hash === 'support' || hash === 'resources' || hash === 'faq') $(hash).scrollIntoView({block: 'start'});
    }
  }

  async function copy(text, message) {
    try {
      await navigator.clipboard.writeText(text);
      $('toast').textContent = message;
      $('toast').hidden = false;
      clearTimeout(toastTimer);
      toastTimer = setTimeout(() => { $('toast').hidden = true; }, 3000);
    } catch (_) {
      $('copy-text').value = text;
      $('copy-dialog').showModal();
      $('copy-text').select();
    }
  }

  $('categories').addEventListener('click', event => {
    const button = event.target.closest('[data-category]');
    if (!button) return;
    category = button.dataset.category;
    history.replaceState(null, '', category === 'all' ? '#faq' : '#category-' + category);
    filter();
  });
  $('search').addEventListener('input', filter);
  $('clear-search').addEventListener('click', () => { $('search').value = ''; filter(); $('search').focus(); });
  $('reset-search').addEventListener('click', () => { category = 'all'; $('search').value = ''; filter(); $('search').focus(); });
  $('expand-all').addEventListener('click', () => answers.filter(answer => !answer.hidden).forEach(answer => { answer.open = true; }));
  $('collapse-all').addEventListener('click', () => answers.filter(answer => !answer.hidden).forEach(answer => { answer.open = false; }));
  $('answers').addEventListener('click', event => {
    const answerButton = event.target.closest('[data-copy-answer]');
    if (answerButton) {
      const faq = byId.get(answerButton.dataset.copyAnswer);
      copy('## ' + faq.title + '\n\n' + faq.body, 'Answer copied.');
    }
    const linkButton = event.target.closest('[data-copy-link]');
    if (linkButton) {
      const url = new URL(location.href);
      url.hash = 'faq-' + linkButton.dataset.copyLink;
      copy(url.href, 'Link copied. Share this answer anywhere.');
    }
  });
  $('copy-report').addEventListener('click', () => copy($('report-template').textContent, 'Report template copied.'));
  document.addEventListener('keydown', event => {
    const editable = /^(INPUT|TEXTAREA|SELECT)$/.test(document.activeElement.tagName) || document.activeElement.isContentEditable;
    if (event.key === '/' && !editable && !event.ctrlKey && !event.metaKey && !event.altKey) { event.preventDefault(); showSection('faq'); $('search').focus(); }
    if (event.key === 'Escape' && document.activeElement === $('search')) { $('search').value = ''; filter(); }
  });
  window.addEventListener('hashchange', route);
  document.documentElement.classList.add('js-enabled');
  filter();
  route();
})();
