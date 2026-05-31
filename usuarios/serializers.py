"""
Serializers de la app usuarios.

- CarreraSerializer      → lista de carreras para el registro
- UsuarioSerializer      → datos del usuario logueado (salida)
- RegistroSerializer     → valida y crea cuenta nueva (entrada)
- LoginSerializer        → valida matrícula + contraseña (entrada)
"""
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.db import IntegrityError, transaction
from rest_framework import serializers

from .models import Carrera, PerfilAlumno


class CarreraSerializer(serializers.ModelSerializer):
    class Meta:
        model = Carrera
        fields = ['id', 'nombre']


class UsuarioSerializer(serializers.Serializer):
    """Convierte un User (+ su PerfilAlumno) al JSON del frontend."""

    id = serializers.IntegerField(read_only=True)
    username = serializers.CharField(read_only=True)
    nombre = serializers.CharField(read_only=True)
    apellido = serializers.CharField(read_only=True)
    correo = serializers.EmailField(read_only=True)
    es_staff = serializers.BooleanField(read_only=True)
    tipo = serializers.CharField(read_only=True)
    matricula = serializers.CharField(read_only=True)
    carrera = serializers.CharField(read_only=True)
    carrera_id = serializers.IntegerField(read_only=True, allow_null=True)
    telefono = serializers.CharField(read_only=True)

    def to_representation(self, user):
        perfil = getattr(user, 'perfil_alumno', None)
        return {
            'id': user.id,
            'username': user.username,
            'nombre': user.first_name,
            'apellido': user.last_name,
            'correo': user.email,
            'es_staff': user.is_staff,
            'tipo': perfil.tipo if perfil else '',
            'matricula': perfil.matricula if perfil else '',
            'carrera': perfil.carrera.nombre if perfil and perfil.carrera else '',
            'carrera_id': perfil.carrera_id if perfil else None,
            'telefono': perfil.telefono if perfil else '',
        }


class RegistroSerializer(serializers.Serializer):
    """Valida los datos del formulario de registro y crea User + PerfilAlumno."""

    tipo = serializers.ChoiceField(
        choices=[PerfilAlumno.TIPO_ALUMNO, PerfilAlumno.TIPO_PROFESOR],
        default=PerfilAlumno.TIPO_ALUMNO,
    )
    nombre = serializers.CharField(max_length=150)
    apellido = serializers.CharField(max_length=150)
    matricula = serializers.CharField(max_length=50)
    correo = serializers.EmailField()
    password = serializers.CharField(min_length=8, write_only=True)
    carrera_id = serializers.IntegerField(required=False, allow_null=True)
    telefono = serializers.CharField(required=False, allow_blank=True, default='')

    def validate_matricula(self, value):
        matricula = value.strip()
        if User.objects.filter(username=matricula).exists():
            raise serializers.ValidationError('Ya existe una cuenta con esa matrícula.')
        return matricula

    def validate_correo(self, value):
        correo = value.strip().lower()
        if User.objects.filter(email__iexact=correo).exists():
            raise serializers.ValidationError('Ya existe una cuenta con ese correo.')
        return correo

    def validate_telefono(self, value):
        return ''.join(ch for ch in str(value or '') if ch.isdigit())

    def validate(self, data):
        if data['tipo'] == PerfilAlumno.TIPO_ALUMNO and not data.get('carrera_id'):
            raise serializers.ValidationError({'carrera_id': 'La carrera es obligatoria para alumnos.'})
        return data

    def create(self, validated_data):
        tipo = validated_data['tipo']
        matricula = validated_data['matricula']
        carrera = None

        if tipo == PerfilAlumno.TIPO_ALUMNO:
            try:
                carrera = Carrera.objects.get(id=validated_data['carrera_id'], activa=True)
            except Carrera.DoesNotExist:
                raise serializers.ValidationError({'carrera_id': 'Carrera no válida.'})

        try:
            with transaction.atomic():
                user = User.objects.create_user(
                    username=matricula,
                    email=validated_data['correo'],
                    password=validated_data['password'],
                    first_name=validated_data['nombre'].strip(),
                    last_name=validated_data['apellido'].strip(),
                )
                PerfilAlumno.objects.create(
                    usuario=user,
                    matricula=matricula,
                    tipo=tipo,
                    carrera=carrera,
                    telefono=validated_data.get('telefono', ''),
                )
        except IntegrityError:
            raise serializers.ValidationError('No se pudo crear la cuenta. Intenta de nuevo.')

        return user


class LoginSerializer(serializers.Serializer):
    matricula = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        request = self.context.get('request')
        user = authenticate(
            request,
            username=data['matricula'].strip(),
            password=data['password'],
        )
        if user is None:
            raise serializers.ValidationError('Matrícula o contraseña incorrectos.')
        data['user'] = user
        return data
