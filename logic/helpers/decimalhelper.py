import decimal


def round_down( value, decimals ):
    with decimal.localcontext() as ctx:
        d = decimal.Decimal( value )

        if type( value ) is int:
            return d

        if str( value ).find( '.' ) == -1:
            return int( value )

        integer_part = str( d ).split( '.' )[ 0 ]

        if decimal.Decimal( integer_part ) != 0:
            decimals = decimals + len( integer_part )

        ctx.prec = decimals
        ctx.rounding = decimal.ROUND_DOWN

        return d.normalize()
