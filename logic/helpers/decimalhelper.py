import decimal


def round_down( value, decimals ):
    with decimal.localcontext() as ctx:
        if type( value ) is float:
            value = str( value )

        d = decimal.Decimal( value )

        if type( value ) is int:
            return d

        if str( value ).find( '.' ) == -1:
            return int( value )

        integer_part = str( d ).split( '.' )[ 0 ]

        if decimal.Decimal( integer_part ) != 0:
            decimals += len( integer_part )

        if str( d.normalize() ).lower().find( 'e' ) != -1:
            return decimal.Decimal( integer_part )

        ctx.prec = decimals
        ctx.rounding = decimal.ROUND_DOWN

        return ctx.create_decimal( value ).normalize()
