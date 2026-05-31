/* ==========================================================================
   footer.js
   Inyecta el pie de página dentro de <footer id="footer"></footer>.
   ========================================================================== */

function construirFooter() {
  var anio = new Date().getFullYear();
  var html =
    '<div class="footer__contenedor">' +
      '<h3 class="footer__titulo">UAdeO Tienda Lince</h3>' +
      '<p class="footer__texto">Universidad Autónoma de Occidente - Región El Fuerte</p>' +
      '<p class="footer__texto">Modalidad Semiescolarizada</p>' +
      '<p class="footer__texto" style="margin-top: 0.75rem;">© ' + anio + ' UAdeO. Proyecto escolar.</p>' +
    '</div>';
  return html;
}

function inicializarFooter() {
  var contenedor = document.getElementById('footer');
  if (!contenedor) {
    console.warn('No se encontró <footer id="footer"></footer> en la página.');
    return;
  }
  contenedor.className = 'footer';
  contenedor.innerHTML = construirFooter();
}
