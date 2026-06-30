document.addEventListener('DOMContentLoaded', function () {
    function getSubtype() {
        var sel = document.getElementById('id_product_subtype');
        return sel ? sel.value : 'ticket';
    }
    function getHasChild() {
        var cb = document.getElementById('id_has_child_ticket');
        return cb ? cb.checked : false;
    }

    function toggleFields() {
        var isTicket = getSubtype() === 'ticket';
        var hasChild = getHasChild();

        // "Có giá vé trẻ em?" — chỉ hiện khi loại = Vé/Combo
        var hasChildRow = document.querySelector('.field-has_child_ticket');
        if (hasChildRow) hasChildRow.style.display = isTicket ? '' : 'none';

        // "Giá vé trẻ em" — chỉ hiện khi Vé/Combo VÀ đã tick "Có giá trẻ em"
        var childPriceRow = document.querySelector('.field-price_child');
        if (childPriceRow) childPriceRow.style.display = (isTicket && hasChild) ? '' : 'none';

        // Đổi nhãn "Giá" theo loại sản phẩm
        var priceLabel = document.querySelector('.field-price label');
        if (priceLabel) {
            priceLabel.textContent = isTicket ? 'Giá vé người lớn' : 'Giá';
        }
    }

    var subtypeSel = document.getElementById('id_product_subtype');
    if (subtypeSel) subtypeSel.addEventListener('change', toggleFields);

    var hasChildCb = document.getElementById('id_has_child_ticket');
    if (hasChildCb) hasChildCb.addEventListener('change', toggleFields);

    toggleFields();
});
