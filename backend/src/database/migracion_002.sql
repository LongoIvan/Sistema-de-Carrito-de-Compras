BEGIN;

ALTER TABLE public.producto
ADD CONSTRAINT chk_producto_stock
CHECK (stock >= 0);

ALTER TABLE public.producto
ADD CONSTRAINT chk_producto_precio
CHECK (precio > 0);

ALTER TABLE public.item_carrito
ADD CONSTRAINT chk_item_cantidad
CHECK (cantidad > 0);

ALTER TABLE public.item_carrito
ADD CONSTRAINT chk_item_precio
CHECK (precio_unitario > 0);

ALTER TABLE public.item_carrito
ADD CONSTRAINT uq_carrito_producto
UNIQUE (idcarrito, id_item_producto);

COMMIT;