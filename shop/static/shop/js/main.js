(function(){
  "use strict";

  const $ = sel => document.querySelector(sel);
  const $all = sel => document.querySelectorAll(sel);

  function csrfHeaders(){
    return {
      "X-CSRFToken": window.CSRF_TOKEN,
      "X-Requested-With": "XMLHttpRequest"
    };
  }
  function postForm(url, data){
    const body = new URLSearchParams(data);
    return fetch(url, { method: "POST", headers: csrfHeaders(), body }).then(r => r.json());
  }

  function showToast(msg){
    const t = $("#toast");
    if(!t) return;
    t.textContent = msg;
    t.classList.add("show");
    clearTimeout(showToast._t);
    showToast._t = setTimeout(()=>t.classList.remove("show"), 2600);
  }

  const fmt = n => "\u20B9" + Math.round(Number(n));

  /* ---------------- Cart drawer ---------------- */
  function openCart(){ $("#cartDrawer").classList.add("open"); $("#cartOverlay").classList.add("open"); }
  function closeCart(){ $("#cartDrawer").classList.remove("open"); $("#cartOverlay").classList.remove("open"); }

  function refreshCartUI(data){
    $("#cartCount").textContent = data.count;
    $("#sumItems").textContent = data.count;
    $("#sumTotal").textContent = fmt(data.total);
    const btn = $("#checkoutBtn");
    if(btn){ btn.classList.toggle("disabled", data.count === 0); }

    const body = $("#cartBody");
    if(!body) return;
    if(data.items.length === 0){
      body.innerHTML = '<div class="empty-note">Your cart is empty. Add some fresh dairy!</div>';
    } else {
      body.innerHTML = data.items.map(e => `
        <div class="cart-item">
          ${e.image_url ? `<img src="${e.image_url}" alt="${e.name}">` : ""}
          <div class="cart-item-info">
            <h4>${e.name}</h4>
            <div class="unit">${e.size} &middot; ${fmt(e.unit_price)} each</div>
            <div class="cart-item-row">
              <div class="qty-stepper">
                <button data-act="dec" data-variant-id="${e.variant_id}">&minus;</button>
                <span>${e.qty}</span>
                <button data-act="inc" data-variant-id="${e.variant_id}">+</button>
              </div>
              <span class="line-total">${fmt(e.line_total)}</span>
            </div>
            <button class="remove-link" data-variant-id="${e.variant_id}" data-act="remove">Remove</button>
          </div>
        </div>`).join("");
    }
    bindCartRowButtons();

    // sync any visible product-grid steppers / pills with new quantities
    if(data.quantities){
      $all(".product-card").forEach(card=>{
        const foot = card.querySelector("[data-foot-for]");
        if(!foot) return;
        const activePill = card.querySelector(".size-pill.active");
        const vid = activePill ? activePill.dataset.variantId : null;
        if(!vid) return;
        const qty = data.quantities[vid] || 0;
        renderCardFoot(foot, vid, qty);
      });
    }
  }

  function renderCardFoot(foot, variantId, qty){
    if(qty > 0){
      foot.innerHTML = `
        <div class="qty-stepper">
          <button data-act="dec" data-variant-id="${variantId}">&minus;</button>
          <span>${qty}</span>
          <button data-act="inc" data-variant-id="${variantId}">+</button>
        </div>`;
    } else {
      foot.innerHTML = `<button class="add-btn" data-act="add" data-variant-id="${variantId}">Add to Cart</button>`;
    }
    bindFootButtons(foot);
  }

  function bindFootButtons(scope){
    scope.querySelectorAll("[data-act='add']").forEach(b=>{
      b.addEventListener("click", ()=> addToCart(b.dataset.variantId));
    });
    scope.querySelectorAll("[data-act='inc']").forEach(b=>{
      b.addEventListener("click", ()=> changeQty(b.dataset.variantId, 1));
    });
    scope.querySelectorAll("[data-act='dec']").forEach(b=>{
      b.addEventListener("click", ()=> changeQty(b.dataset.variantId, -1));
    });
  }

  function bindCartRowButtons(){
    bindFootButtons($("#cartBody"));
    $all("#cartBody [data-act='remove']").forEach(b=>{
      b.addEventListener("click", ()=>{
        postForm(window.URLS.cartRemove, {variant_id: b.dataset.variantId}).then(refreshCartUI);
      });
    });
  }

  function addToCart(variantId){
    postForm(window.URLS.cartAdd, {variant_id: variantId}).then(data=>{
      if(!data.ok){ showToast(data.error || "Could not add to cart."); return; }
      refreshCartUI(data);
      showToast("Added to cart");
    });
  }
  function changeQty(variantId, delta){
    postForm(window.URLS.cartChange, {variant_id: variantId, delta}).then(refreshCartUI);
  }

  function loadCartSummary(){
    fetch(window.URLS.cartSummary).then(r=>r.json()).then(refreshCartUI);
  }

  /* ---------------- Product grid: size pill selection ---------------- */
  function bindSizePills(){
    $all(".size-pills[data-pid]").forEach(group=>{
      group.querySelectorAll(".size-pill").forEach(pill=>{
        pill.addEventListener("click", ()=>{
          group.querySelectorAll(".size-pill").forEach(p=>p.classList.remove("active"));
          pill.classList.add("active");
          const pid = group.dataset.pid;
          const price = pill.dataset.price;
          const priceEl = document.querySelector(`[data-price-for="${pid}"]`);
          if(priceEl) priceEl.textContent = fmt(price);
          const foot = document.querySelector(`[data-foot-for="${pid}"]`);
          if(foot){
            // check current cart quantity for this variant via a summary refresh
            fetch(window.URLS.cartSummary).then(r=>r.json()).then(data=>{
              const qty = (data.quantities && data.quantities[pill.dataset.variantId]) || 0;
              renderCardFoot(foot, pill.dataset.variantId, qty);
            });
          }
        });
      });
    });
  }

  /* ---------------- Owner dashboard: inline auto-save fields ---------------- */
  function bindInlineAdminFields(){
    $all("input[data-url]").forEach(input=>{
      let original = input.value;
      input.addEventListener("change", ()=>{
        const url = input.dataset.url;
        const field = input.dataset.field || "value";
        const payload = { [field]: input.value };
        if(input.dataset.extraField){
          payload.field = input.dataset.extraField;
        }
        postForm(url, payload).then(data=>{
          if(data.ok){
            showToast("Saved");
            original = input.value;
          } else {
            showToast(data.error || "Could not save change.");
            input.value = original;
          }
        }).catch(()=>{
          showToast("Network error while saving.");
          input.value = original;
        });
      });
    });
  }

  /* ---------------- Init ---------------- */
  document.addEventListener("DOMContentLoaded", function(){
    const openBtn = $("#openCartBtn");
    const closeBtn = $("#closeCartBtn");
    const continueBtn = $("#continueBtn");
    const overlay = $("#cartOverlay");
    if(openBtn) openBtn.addEventListener("click", openCart);
    if(closeBtn) closeBtn.addEventListener("click", closeCart);
    if(continueBtn) continueBtn.addEventListener("click", closeCart);
    if(overlay) overlay.addEventListener("click", closeCart);

    if($("#cartBody")) loadCartSummary();
    bindSizePills();
    bindInlineAdminFields();

    // top-level (non-pill) add/inc/dec buttons already on the page at load
    bindFootButtons(document);
  });
})();
