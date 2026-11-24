BEGIN;

ALTER TABLE public.carrito
DROP CONSTRAINT fk_carrito_usuario;

ALTER TABLE public.carrito
ADD CONSTRAINT fk_carrito_usuario
FOREIGN KEY (idusuario)
REFERENCES public.usuario(idusuario)
ON DELETE RESTRICT;

COMMIT;