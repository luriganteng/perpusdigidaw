// PerpusDigi — interaksi kecil di sisi klien (toggle menu mobile)
document.addEventListener('DOMContentLoaded', function () {
  var toggle = document.getElementById('navToggle');
  var sidebar = document.getElementById('sidebar');
  var overlay = document.getElementById('sidebarOverlay');

  if (!toggle || !sidebar || !overlay) return;

  function openNav() {
    sidebar.classList.add('open');
    overlay.classList.add('visible');
    toggle.setAttribute('aria-expanded', 'true');
  }

  function closeNav() {
    sidebar.classList.remove('open');
    overlay.classList.remove('visible');
    toggle.setAttribute('aria-expanded', 'false');
  }

  toggle.addEventListener('click', function () {
    if (sidebar.classList.contains('open')) {
      closeNav();
    } else {
      openNav();
    }
  });

  overlay.addEventListener('click', closeNav);

  // Tutup menu otomatis begitu salah satu link diklik (biar gak nutupin halaman baru)
  sidebar.querySelectorAll('.nav a').forEach(function (a) {
    a.addEventListener('click', closeNav);
  });

  // Tutup menu kalau layar di-resize balik ke ukuran desktop
  window.addEventListener('resize', function () {
    if (window.innerWidth > 900) closeNav();
  });
});
