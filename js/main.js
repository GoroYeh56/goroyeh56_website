/* ===== GOROYEH56 - MAIN.JS ===== */

document.addEventListener('DOMContentLoaded', () => {

  // ── Hero load animation
  const hero = document.getElementById('hero');
  if (hero) setTimeout(() => hero.classList.add('loaded'), 100);

  // ── Navbar scroll effect
  const navbar = document.getElementById('navbar');
  window.addEventListener('scroll', () => {
    navbar.classList.toggle('scrolled', window.scrollY > 40);
  }, { passive: true });

  // ── Mobile nav toggle
  const navToggle = document.getElementById('navToggle');
  const navLinks  = document.getElementById('navLinks');
  navToggle?.addEventListener('click', () => navLinks.classList.toggle('open'));
  navLinks?.querySelectorAll('a').forEach(a => a.addEventListener('click', () => navLinks.classList.remove('open')));

  // ── About slider
  const slides     = Array.from(document.querySelectorAll('.slide'));
  const dotsWrap   = document.getElementById('sliderDots');
  let current      = 0;
  let sliderTimer  = null;

  if (slides.length && dotsWrap) {
    slides.forEach((_, i) => {
      const btn = document.createElement('button');
      btn.className = 'dot' + (i === 0 ? ' active' : '');
      btn.setAttribute('aria-label', `Slide ${i + 1}`);
      btn.addEventListener('click', () => goSlide(i));
      dotsWrap.appendChild(btn);
    });

    const goSlide = (idx) => {
      slides[current].classList.remove('active');
      dotsWrap.children[current].classList.remove('active');
      current = (idx + slides.length) % slides.length;
      slides[current].classList.add('active');
      dotsWrap.children[current].classList.add('active');
      resetTimer();
    };

    const resetTimer = () => {
      clearInterval(sliderTimer);
      sliderTimer = setInterval(() => goSlide(current + 1), 4500);
    };

    document.getElementById('sliderPrev')?.addEventListener('click', () => goSlide(current - 1));
    document.getElementById('sliderNext')?.addEventListener('click', () => goSlide(current + 1));
    resetTimer();
  }

  // ── Bookshelf data
  const books = [
    { title: 'Hidden Potential', author: 'Adam Grant', status: 'finished', color: '#f5ede3', textColor: '#8B6A3E', cover: 'https://images.unsplash.com/photo-1589829085413-56de8ae18c73?w=300&q=80' },
    { title: "Can't Hurt Me", author: 'David Goggins', status: 'finished', color: '#1a1a1a', textColor: '#ffffff', cover: 'https://images.unsplash.com/photo-1512820790803-83ca734da794?w=300&q=80' },
    { title: 'Think and Grow Rich', author: 'Napoleon Hill', status: 'finished', color: '#1a1a1a', textColor: '#d4a843', cover: 'https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c?w=300&q=80' },
    { title: '從工程師到旅行者', author: '張J', status: 'finished', color: '#2d2d2d', textColor: '#ffffff', cover: 'https://images.unsplash.com/photo-1501854140801-50d01698950b?w=300&q=80' },
    { title: '親密恐懼', author: '周慕姿', status: 'finished', color: '#f8ede0', textColor: '#8a6a4a', cover: 'https://images.unsplash.com/photo-1474631245212-32dc3c8310c6?w=300&q=80' },
    { title: '我，刀槍不入', author: 'David Goggins', status: 'finished', color: '#111', textColor: '#e63946', cover: 'https://images.unsplash.com/photo-1541534741688-6078c6bfb5c5?w=300&q=80' },
    { title: 'Zero to One', author: 'Peter Thiel', status: 'finished', color: '#0a0a0a', textColor: '#ffffff', cover: 'https://images.unsplash.com/photo-1568667256549-094345857637?w=300&q=80' },
    { title: 'The Almanack of Naval Ravikant', author: 'Eric Jorgenson', status: 'reading', color: '#f0f4f8', textColor: '#2d3748', cover: 'https://images.unsplash.com/photo-1543002588-bfa74002ed7e?w=300&q=80' },
    { title: 'Atomic Habits', author: 'James Clear', status: 'reading', color: '#e6f3ff', textColor: '#1a5276', cover: 'https://images.unsplash.com/photo-1481627834876-b7833e8f5570?w=300&q=80' },
    { title: 'Deep Work', author: 'Cal Newport', status: 'want', color: '#e8f5e9', textColor: '#1b5e20', cover: 'https://images.unsplash.com/photo-1533090161767-e6ffed986c88?w=300&q=80' },
    { title: 'The Lean Startup', author: 'Eric Ries', status: 'want', color: '#fff3e0', textColor: '#e65100', cover: 'https://images.unsplash.com/photo-1553729459-efe14ef6055d?w=300&q=80' },
    { title: 'Sapiens', author: 'Yuval Noah Harari', status: 'want', color: '#fce4ec', textColor: '#880e4f', cover: 'https://images.unsplash.com/photo-1524995997946-a1c2e315a42f?w=300&q=80' },
  ];

  const statusLabel = { finished: 'Finished', reading: 'Reading', want: 'Want to Read' };
  const booksGrid = document.getElementById('booksGrid');

  const renderBooks = (filter = 'all') => {
    if (!booksGrid) return;
    booksGrid.innerHTML = '';
    books.forEach(book => {
      const visible = filter === 'all' || book.status === filter;
      const card = document.createElement('div');
      card.className = 'book-card fade-in' + (visible ? '' : ' hidden');
      card.setAttribute('data-status', book.status);
      card.innerHTML = `
        <div class="book-cover">
          <img src="${book.cover}" alt="${book.title}" loading="lazy"
               onerror="this.style.display='none'; this.parentElement.style.background='${book.color}'; this.parentElement.style.display='flex'; this.parentElement.style.alignItems='center'; this.parentElement.style.justifyContent='center'; this.parentElement.innerHTML='<span style=\'font-size:0.7rem;font-weight:600;padding:0.75rem;text-align:center;color:${book.textColor};line-height:1.3;\'>${book.title}</span>';"/>
        </div>
        <div class="book-status">${statusLabel[book.status]}</div>
        <div class="book-title">${book.title}</div>
        <div class="book-author">${book.author}</div>
      `;
      booksGrid.appendChild(card);
    });
    setTimeout(() => {
      booksGrid.querySelectorAll('.book-card:not(.hidden)').forEach((el, i) => {
        setTimeout(() => el.classList.add('visible'), i * 60);
      });
    }, 50);
  };

  renderBooks();

  document.querySelectorAll('.filter-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      renderBooks(btn.dataset.filter);
    });
  });

  // ── Draw world map (SVG simplified continents + visited pins)
  const visitedCoords = [
    { name: 'Taiwan', x: 780, y: 230, visited: true },
    { name: 'Japan', x: 810, y: 200, visited: true },
    { name: 'USA', x: 180, y: 205, visited: true },
    { name: 'South Korea', x: 793, y: 210, visited: true },
    { name: 'China', x: 750, y: 210, visited: true },
    { name: 'Alaska', x: 120, y: 150, visited: true },
  ];

  const mapSvg = document.getElementById('worldMap');
  if (mapSvg) {
    // Simple world outline paths (approximate)
    const landMasses = [
      // North America
      { d: 'M 100 120 L 280 100 L 310 130 L 300 200 L 260 240 L 200 280 L 160 300 L 120 270 L 80 230 L 70 180 Z', label: 'NA' },
      // South America
      { d: 'M 200 290 L 270 280 L 300 320 L 290 400 L 250 440 L 200 430 L 175 380 L 180 320 Z', label: 'SA' },
      // Europe
      { d: 'M 450 100 L 540 90 L 570 120 L 560 160 L 510 165 L 480 155 L 450 145 Z', label: 'EU' },
      // Africa
      { d: 'M 470 170 L 570 160 L 590 200 L 580 300 L 550 360 L 510 380 L 480 360 L 460 290 L 450 210 Z', label: 'AF' },
      // Asia
      { d: 'M 570 90 L 830 80 L 860 150 L 840 240 L 790 260 L 720 240 L 660 220 L 620 200 L 580 180 L 560 150 Z', label: 'AS' },
      // Oceania
      { d: 'M 770 290 L 860 280 L 880 330 L 850 370 L 800 365 L 770 340 Z', label: 'OC' },
    ];

    landMasses.forEach(({ d, label }) => {
      const path = document.createElementNS('http://www.w3.org/2000/svg', 'path');
      path.setAttribute('d', d);
      path.setAttribute('fill', '#e8e4dc');
      path.setAttribute('stroke', '#fff');
      path.setAttribute('stroke-width', '1.5');
      mapSvg.appendChild(path);
    });

    visitedCoords.forEach(({ x, y, visited, name }) => {
      const g = document.createElementNS('http://www.w3.org/2000/svg', 'g');

      if (visited) {
        const pulse = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
        pulse.setAttribute('cx', x); pulse.setAttribute('cy', y);
        pulse.setAttribute('r', '8'); pulse.setAttribute('fill', 'rgba(200,146,42,0.2)');
        g.appendChild(pulse);
      }

      const dot = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
      dot.setAttribute('cx', x); dot.setAttribute('cy', y);
      dot.setAttribute('r', '5');
      dot.setAttribute('fill', visited ? '#c8922a' : '#b0a898');
      dot.setAttribute('stroke', '#fff');
      dot.setAttribute('stroke-width', '1.5');

      const title = document.createElementNS('http://www.w3.org/2000/svg', 'title');
      title.textContent = name;
      dot.appendChild(title);
      g.appendChild(dot);
      mapSvg.appendChild(g);
    });
  }

  // ── Intersection observer for fade-in
  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add('visible');
        observer.unobserve(entry.target);
      }
    });
  }, { threshold: 0.12, rootMargin: '0px 0px -40px 0px' });

  document.querySelectorAll('.channel-card, .blog-featured, .blog-item, .photo-item, .country-chip, .blog-medium-card').forEach(el => {
    el.classList.add('fade-in');
    observer.observe(el);
  });

  // ── Contact form (AJAX)
  const form = document.getElementById('contactForm');
  const status = document.getElementById('formStatus');

  form?.addEventListener('submit', async (e) => {
    e.preventDefault();
    const btn = form.querySelector('button[type="submit"]');
    btn.disabled = true;
    btn.textContent = 'Sending…';
    status.className = 'form-status';
    status.textContent = '';

    const data = new FormData(form);

    try {
      const res = await fetch('contact.php', { method: 'POST', body: data });
      const json = await res.json();
      if (json.success) {
        status.className = 'form-status success';
        status.textContent = '✓ Message sent! I\'ll get back to you soon.';
        form.reset();
      } else {
        throw new Error(json.message || 'Error');
      }
    } catch (err) {
      status.className = 'form-status error';
      status.textContent = 'Something went wrong. Please email me directly at goroyeh56@gmail.com';
    }

    btn.disabled = false;
    btn.textContent = 'Send Message →';
  });

  // ── Smooth active nav link highlight on scroll
  const sections = document.querySelectorAll('section[id]');
  const navAnchors = document.querySelectorAll('.nav-links a[href^="#"]');

  window.addEventListener('scroll', () => {
    let current = '';
    sections.forEach(sec => {
      if (window.scrollY >= sec.offsetTop - 120) current = sec.id;
    });
    navAnchors.forEach(a => {
      a.style.color = a.getAttribute('href') === `#${current}` ? 'var(--text)' : '';
    });
  }, { passive: true });

  // ── Live Recent Posts via local PHP proxy (no third-party API) ────
  const RSS_URL = '/rss-proxy.php';

  // Category tag color map — matches WordPress categories exactly
  const tagColors = {
    'machine learning':       { bg: '#e3f2fd', color: '#1565c0', label: 'Machine Learning' },
    'life':                   { bg: '#e8f5e9', color: '#2e7d32', label: 'Life' },
    'c++':                    { bg: '#f3e5f5', color: '#6a1b9a', label: 'C++' },
    'photography and travel': { bg: '#fff3e0', color: '#b45309', label: 'Photography & Travel' },
    'reading':                { bg: '#fce4ec', color: '#9d174d', label: 'Reading' },
    'sports':                 { bg: '#ecfdf5', color: '#065f46', label: 'Sports' },
    'uncategorized':          { bg: '#f5f5f5', color: '#6b7280', label: 'Uncategorized' },
  };

  const getTag = (categories) => {
    if (!categories || !categories.length) return null;
    const key = categories[0].toLowerCase();
    return tagColors[key] || { bg: '#f5f5f5', color: '#555', label: categories[0] };
  };

  const formatDate = (dateStr) => {
    const d = new Date(dateStr);
    return d.toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' });
  };

  const estimateReadTime = (content) => {
    const words = content?.replace(/<[^>]+>/g, '').split(/\s+/).length || 0;
    return Math.max(1, Math.round(words / 200)) + ' min read';
  };

  const fetchRSS = async () => {
    try {
      const res  = await fetch(`${RSS_URL}?count=6&_=${Date.now()}`);
      const data = await res.json();

      if (data.status !== 'ok' || !data.items?.length) return;

      const items = data.items;

      // ── Featured post (first item)
      const featured = items[0];
      const featuredEl = document.querySelector('.blog-featured');
      if (featuredEl) {
        const img    = featured.thumbnail || featured.enclosure?.link || '';
        const cats   = featured.categories || [];
        const tag    = getTag(cats);
        const date   = formatDate(featured.pubDate);
        const read   = estimateReadTime(featured.content);

        featuredEl.innerHTML = `
          <a href="${featured.link}" target="_blank" class="blog-featured-link">
            <div class="blog-featured-img" style="${!img ? 'background:#e5e3df;min-height:260px;' : ''}">
              ${img ? `<img src="${img}" alt="${featured.title}" loading="lazy"/>` : '<div style="height:260px;background:var(--bg2);border-radius:var(--radius);"></div>'}
              ${tag ? `<span class="blog-tag" style="background:${tag.bg};color:${tag.color}">${tag.label}</span>` : ''}
            </div>
            <div class="blog-featured-body">
              <h3>${featured.title}</h3>
              <p class="blog-meta">${date} · ${read}</p>
            </div>
          </a>`;
      }

      // ── Side list (next 3 items)
      const blogList = document.querySelector('.blog-list');
      if (blogList) {
        // Keep the Medium card if it exists, rebuild the post items
        const mediumCard = blogList.querySelector('.blog-medium-card');
        blogList.innerHTML = '';

        items.slice(1, 4).forEach(item => {
          const cats = item.categories || [];
          const tag  = getTag(cats);
          const date = formatDate(item.pubDate);
          const el   = document.createElement('a');
          el.href   = item.link;
          el.target = '_blank';
          el.className = 'blog-item fade-in';
          el.innerHTML = `
            ${tag ? `<span class="blog-tag" style="background:${tag.bg};color:${tag.color}">${tag.label}</span>` : ''}
            <h4>${item.title}</h4>
            <p class="blog-meta">${date}</p>`;
          blogList.appendChild(el);
        });

        // Re-append Medium card
        if (mediumCard) blogList.appendChild(mediumCard);

        // Re-observe new elements
        blogList.querySelectorAll('.blog-item').forEach(el => observer.observe(el));
      }

    } catch (err) {
      // Silently fail — static fallback content stays visible
      console.warn('RSS fetch failed, showing static fallback.', err);
    }
  };

  fetchRSS();

  // ── Photo Grid — auto-fetch from photo-proxy.php ─────────────────
  const photoGrid = document.getElementById('photoGrid');

  const buildPhotoGrid = (photos) => {
    if (!photoGrid || !photos?.length) return;
    photoGrid.innerHTML = '';
    photos.forEach((photo, idx) => {
      const div = document.createElement('div');
      div.className = 'photo-item';
      div.dataset.full    = photo.full;
      div.dataset.caption = photo.caption || '';
      if (photo.link) div.dataset.postLink = photo.link;
      div.innerHTML = `<img src="${photo.thumb}" alt="${photo.caption || 'Photo by Goro Yeh'}" loading="lazy"/>`;
      div.addEventListener('click', () => openLb(idx));
      photoGrid.appendChild(div);
    });
  };

  const fetchPhotos = async () => {
    try {
      const res  = await fetch(`/photo-proxy.php?count=12&_=${Date.now()}`);
      const data = await res.json();
      if (data.status === 'ok' && data.photos?.length) {
        buildPhotoGrid(data.photos);
        // Re-observe new photo items for fade-in
        photoGrid.querySelectorAll('.photo-item').forEach(el => {
          el.classList.add('fade-in');
          observer.observe(el);
        });
      }
    } catch (err) {
      console.warn('Photo fetch failed, keeping static grid.', err);
    }
  };

  fetchPhotos();

  // ── Lightbox ─────────────────────────────────────────────────────
  const lb        = document.getElementById('lightbox');
  const lbImg     = document.getElementById('lbImg');
  const lbSpinner = document.getElementById('lbSpinner');
  const lbCaption = document.getElementById('lbCaptionText');
  const lbLink    = document.getElementById('lbInstaLink');
  const lbCounter = document.getElementById('lbCounter');

  let lbItems = [];
  let lbIndex = 0;

  const rebuildLbItems = () => {
    lbItems = Array.from(document.querySelectorAll('.photo-item'));
  };

  const openLb = (idx) => {
    rebuildLbItems();
    lbIndex = idx;
    showLbSlide(lbIndex);
    lb.classList.add('active');
    lb.setAttribute('aria-hidden', 'false');
    document.body.style.overflow = 'hidden';
  };

  const closeLb = () => {
    lb.classList.remove('active');
    lb.setAttribute('aria-hidden', 'true');
    document.body.style.overflow = '';
    lbImg.classList.remove('loaded');
    lbImg.src = '';
  };

  const showLbSlide = (idx) => {
    const item    = lbItems[idx];
    const fullSrc = item.dataset.full    || item.querySelector('img')?.src || '';
    const caption = item.dataset.caption || '';
    const postLink = item.dataset.postLink || '';

    lbImg.classList.remove('loaded');
    lbSpinner.classList.remove('hidden');

    const tmp = new Image();
    tmp.onload = () => {
      lbImg.src = fullSrc;
      lbImg.alt = caption;
      lbImg.classList.add('loaded');
      lbSpinner.classList.add('hidden');
    };
    tmp.onerror = () => {
      lbImg.src = item.querySelector('img')?.src || '';
      lbImg.classList.add('loaded');
      lbSpinner.classList.add('hidden');
    };
    tmp.src = fullSrc;

    lbCaption.textContent = caption;
    lbCounter.textContent = `${idx + 1} / ${lbItems.length}`;

    if (postLink) {
      lbLink.href = postLink;
      lbLink.textContent = 'View post →';
      lbLink.classList.add('visible');
    } else {
      lbLink.href = 'https://www.instagram.com/goroyeh56.photography/';
      lbLink.textContent = 'View on Instagram →';
      lbLink.classList.add('visible');
    }
  };

  document.getElementById('lbClose')?.addEventListener('click', closeLb);
  document.getElementById('lbPrev')?.addEventListener('click', () => {
    rebuildLbItems();
    lbIndex = (lbIndex - 1 + lbItems.length) % lbItems.length;
    showLbSlide(lbIndex);
  });
  document.getElementById('lbNext')?.addEventListener('click', () => {
    rebuildLbItems();
    lbIndex = (lbIndex + 1) % lbItems.length;
    showLbSlide(lbIndex);
  });

  lb?.addEventListener('click', (e) => { if (e.target === lb) closeLb(); });

  document.addEventListener('keydown', (e) => {
    if (!lb?.classList.contains('active')) return;
    if (e.key === 'Escape')      { closeLb(); return; }
    if (e.key === 'ArrowLeft')   { rebuildLbItems(); lbIndex = (lbIndex - 1 + lbItems.length) % lbItems.length; showLbSlide(lbIndex); }
    if (e.key === 'ArrowRight')  { rebuildLbItems(); lbIndex = (lbIndex + 1) % lbItems.length; showLbSlide(lbIndex); }
  });

  // Also attach click to any static photo-items already in HTML
  document.querySelectorAll('.photo-item').forEach((item, idx) => {
    item.addEventListener('click', () => openLb(idx));
  });

});
