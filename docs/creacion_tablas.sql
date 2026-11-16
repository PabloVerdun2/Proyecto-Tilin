-- ============================================================
-- GourmetDB - Script de creacion de tablas (generado por Django)
-- Comando: python manage.py sqlmigrate cuentas 0001
-- ============================================================

BEGIN TRANSACTION
--
-- Create model Mesa
--
CREATE TABLE [cuentas_mesa] ([id] bigint NOT NULL PRIMARY KEY IDENTITY (1, 1), [numero] int NOT NULL UNIQUE, [capacidad] int NOT NULL, [disponible] bit NOT NULL);
--
-- Create model CustomUser
--
CREATE TABLE [cuentas_customuser] ([id] bigint NOT NULL PRIMARY KEY IDENTITY (1, 1), [password] nvarchar(128) NOT NULL, [last_login] datetimeoffset NULL, [is_superuser] bit NOT NULL, [email] nvarchar(254) NOT NULL UNIQUE, [first_name] nvarchar(30) NOT NULL, [last_name] nvarchar(30) NOT NULL, [is_active] bit NOT NULL, [is_staff] bit NOT NULL);
CREATE TABLE [cuentas_customuser_groups] ([id] bigint NOT NULL PRIMARY KEY IDENTITY (1, 1), [customuser_id] bigint NOT NULL, [group_id] int NOT NULL);
CREATE TABLE [cuentas_customuser_user_permissions] ([id] bigint NOT NULL PRIMARY KEY IDENTITY (1, 1), [customuser_id] bigint NOT NULL, [permission_id] int NOT NULL);
--
-- Create model Reserva
--
CREATE TABLE [cuentas_reserva] ([id] bigint NOT NULL PRIMARY KEY IDENTITY (1, 1), [fecha] date NOT NULL, [hora] time NOT NULL, [cantidad_personas] int NOT NULL CONSTRAINT cuentas_reserva_cantidad_personas_7eb9554f_check CHECK ([cantidad_personas] >= 0), [motivo] nvarchar(20) NOT NULL, [nombre_contacto] nvarchar(100) NOT NULL, [correo] nvarchar(254) NOT NULL, [telefono] nvarchar(20) NOT NULL, [notas_adicionales] nvarchar(max) NOT NULL, [cliente_id] bigint NOT NULL, [mesa_id] bigint NULL);
CREATE UNIQUE INDEX [cuentas_customuser_groups_customuser_id_group_id_b4835d13_uniq] ON [cuentas_customuser_groups] ([customuser_id], [group_id]) WHERE [customuser_id] IS NOT NULL AND [group_id] IS NOT NULL;
ALTER TABLE [cuentas_customuser_user_permissions] ADD CONSTRAINT [cuentas_customuser_user_permissions_customuser_id_c50469bb_fk_cuentas_customuser_id] FOREIGN KEY ([customuser_id]) REFERENCES [cuentas_customuser] ([id]);
ALTER TABLE [cuentas_customuser_user_permissions] ADD CONSTRAINT [cuentas_customuser_user_permissions_permission_id_ffabfaaf_fk_auth_permission_id] FOREIGN KEY ([permission_id]) REFERENCES [auth_permission] ([id]);
CREATE INDEX [cuentas_reserva_mesa_id_54e2dbab] ON [cuentas_reserva] ([mesa_id]);
CREATE UNIQUE INDEX [cuentas_customuser_user_permissions_customuser_id_permission_id_fd2ddd17_uniq] ON [cuentas_customuser_user_permissions] ([customuser_id], [permission_id]) WHERE [customuser_id] IS NOT NULL AND [permission_id] IS NOT NULL;
ALTER TABLE [cuentas_reserva] ADD CONSTRAINT [cuentas_reserva_mesa_id_54e2dbab_fk_cuentas_mesa_id] FOREIGN KEY ([mesa_id]) REFERENCES [cuentas_mesa] ([id]);
ALTER TABLE [cuentas_customuser_groups] ADD CONSTRAINT [cuentas_customuser_groups_customuser_id_2e1531d8_fk_cuentas_customuser_id] FOREIGN KEY ([customuser_id]) REFERENCES [cuentas_customuser] ([id]);
ALTER TABLE [cuentas_customuser_groups] ADD CONSTRAINT [cuentas_customuser_groups_group_id_d6734166_fk_auth_group_id] FOREIGN KEY ([group_id]) REFERENCES [auth_group] ([id]);
CREATE INDEX [cuentas_reserva_cliente_id_77ffef39] ON [cuentas_reserva] ([cliente_id]);
CREATE INDEX [cuentas_customuser_groups_customuser_id_2e1531d8] ON [cuentas_customuser_groups] ([customuser_id]);
ALTER TABLE [cuentas_reserva] ADD CONSTRAINT [cuentas_reserva_cliente_id_77ffef39_fk_cuentas_customuser_id] FOREIGN KEY ([cliente_id]) REFERENCES [cuentas_customuser] ([id]);
CREATE INDEX [cuentas_customuser_groups_group_id_d6734166] ON [cuentas_customuser_groups] ([group_id]);
CREATE INDEX [cuentas_customuser_user_permissions_customuser_id_c50469bb] ON [cuentas_customuser_user_permissions] ([customuser_id]);
CREATE INDEX [cuentas_customuser_user_permissions_permission_id_ffabfaaf] ON [cuentas_customuser_user_permissions] ([permission_id]);
COMMIT;

-- ------------------------------------------------------------
-- Ajuste posterior (migracion 0003): se agrego la columna estado
-- ------------------------------------------------------------
ALTER TABLE [cuentas_reserva] DROP COLUMN [activa];
-- Add field estado to reserva
ALTER TABLE [cuentas_reserva] ADD [estado] nvarchar(20) DEFAULT 'pendiente' NOT NULL;
SELECT d.name FROM sys.default_constraints d INNER JOIN sys.tables t ON d.parent_object_id = t.object_id INNER JOIN sys.columns c ON d.parent_object_id = c.object_id AND d.parent_column_id = c.column_id INNER JOIN sys.schemas s ON t.schema_id = s.schema_id WHERE t.name = 'cuentas_reserva' AND c.name = 'estado';
ALTER TABLE [cuentas_reserva] DROP CONSTRAINT [estado];
